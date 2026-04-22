import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding='utf-8')

from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.vector_stores.azureaisearch import AzureAISearchVectorStore
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from resource_config import setup_global_llm_and_embedding

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------

# ch03 수동 매핑이 완료된 인덱스
INDEX_NAME = "taping-guide-index-3"

# AutoMergingRetriever가 parent 노드를 복원할 때 참조하는 로컬 docstore
DOCSTORE_PATH = Path(__file__).parent.parent / "data" / "docstore3" / "docstore.json"

# ---------------------------------------------------------------------------
# 추천 옵션 생성용 프롬프트 (llm.complete()로 직접 호출)
# valid_codes: RAG 검색 후 노드 메타데이터에서 동적 추출
# ---------------------------------------------------------------------------

RECOMMENDATION_PROMPT = """\
SYSTEM:
You are a kinesiology taping recommendation assistant.
You will receive (1) a structured symptom, and (2) retrieved textbook passages.
Your job is to recommend taping options and explain WHY each option helps.

=== CRITICAL CONSTRAINTS ===
- You MUST only recommend technique_codes from the VALID SET provided below.
- Do NOT invent techniques outside this list.
- If no technique in the valid set matches, return an empty options array.
- All "why" and "steps.instruction" fields must be grounded in the retrieved passages.
  If a passage does not support a claim, do not make the claim.
- Output ONLY valid JSON. No explanation, no markdown.

=== VALID TECHNIQUE CODES FOR THIS REQUEST ===
{valid_codes}

=== RETRIEVED TEXTBOOK PASSAGES ===
{rag_chunks}

=== STRUCTURED SYMPTOM ===
{structured_symptom}

Output schema:
{{
  "analysis": "전반적인 증상 해석 한 줄",
  "body_part": "입력받은 body_part 그대로",
  "options": [
    {{
      "option_rank": 1,
      "technique_name": "기법 이름 (한글)",
      "technique_code": "VALID TECHNIQUE CODES 중 하나만",
      "body_region": "세부 부위",
      "laterality": "left | right | bilateral",
      "tape_type": "대표 테이프 타입",
      "stretch_pct": 15,
      "position": "준비 자세 (영문 코드)",
      "anchor_position": "앵커 위치 설명",
      "why": "RAG 근거 기반 설명 (한글)",
      "contraindication": "주의사항 (한글)",
      "source_chunk_ids": ["chunk_id_001"],
      "steps": [
        {{
          "step": 1,
          "tape_type": "I-strip",
          "instruction": "step 설명 (한글)"
        }}
      ]
    }}
  ],
  "coaching_text": "사용자에게 전달할 종합 안내 문구 (한글)",
  "disclaimer": "이 서비스는 예방적 셀프케어 가이드예요. 지속되는 증상은 전문가에게 확인해보세요.",
  "history_metadata": {{
    "title": "히스토리 목록 표시용 제목 (15자 내외, 한글)",
    "preview_text": "히스토리 목록 표시용 요약 (30자 내외, 한글)"
  }}
}}

=== SAFETY RULES ===
- If structured_symptom contains "acute": true → return {{"options": [], "redirect": "hospital"}}
- Never mention body parts outside the structured_symptom body_part.
- If retrieved passages are insufficient, set why to: "교본 자료가 제한적이에요. 전문가 확인을 권해요."
- steps: taping procedure 청크의 Step 순서대로. 청크에 없으면 []
- steps.tape_type: 해당 step 실제 사용 타입. 정보 없으면 null
- source_chunk_ids: 실제 사용한 노드 ID만
- 출력은 순수 JSON만 (마크다운 없음)
"""


class TapingRAGSystem:
    def __init__(self):
        setup_global_llm_and_embedding()
        self.llm = Settings.llm
        self._setup_index()

    def _setup_index(self):
        """Azure AI Search 연결 및 로컬 docstore 로드."""
        endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
        key = os.getenv("AZURE_AI_SEARCH_KEY")

        if not endpoint or not key:
            missing = [k for k, v in {
                "AZURE_AI_SEARCH_ENDPOINT": endpoint,
                "AZURE_AI_SEARCH_KEY": key,
            }.items() if not v]
            raise EnvironmentError(
                f"필수 환경변수 누락: {missing}. .env 파일을 확인하세요."
            )

        # technique_code 컬럼 직접 조회용 (valid_codes 추출에 사용)
        self._search_client = SearchClient(
            endpoint=endpoint,
            index_name=INDEX_NAME,
            credential=AzureKeyCredential(key),
        )

        search_client = SearchIndexClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )
        self.vector_store = AzureAISearchVectorStore(
            search_or_index_client=search_client,
            index_name=INDEX_NAME,
            id_field_key="chunk_id",
            chunk_field_key="chunk",
            embedding_field_key="text_vector",
            doc_id_field_key="parent_id",
            metadata_string_field_key="metadata",
            filterable_metadata_field_keys=[
                "source", "body_part", "technique_code", "condition", "body_region",
                "tape_type", "min_stretch", "max_stretch",
            ],
        )
        self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store)

        try:
            self.docstore = SimpleDocumentStore.from_persist_path(str(DOCSTORE_PATH))
            print(f"[INFO] Docstore 로드 완료: {len(self.docstore.docs)}개 노드")
        except Exception as e:
            self.docstore = None
            print(f"[ERROR] Docstore 로드 실패 ({e}). AutoMerging 없이 동작합니다.")

    def _build_retriever(self, filters=None):
        """AutoMergingRetriever 생성. docstore가 없으면 기본 retriever 반환."""
        base_retriever = self.index.as_retriever(similarity_top_k=6, filters=filters)

        if self.docstore is None:
            return base_retriever

        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store,
            docstore=self.docstore,
        )
        return AutoMergingRetriever(base_retriever, storage_context, verbose=True)

    def _translate(self, raw_text: str) -> str:
        """한국어 입력을 영어 의학 용어로 번역 (recommend() 내부 전용).
        LLM 호출 실패 또는 빈 결과 시 원문 반환.
        """
        prompt = (
            "You are a medical translator specializing in kinesiology taping. "
            "Translate the user's Korean input into English medical terms for searching professional documents.\n\n"
            f"Korean: {raw_text}\nEnglish:"
        )
        try:
            response = self.llm.complete(prompt)
            translated = response.text.strip()
        except Exception as e:
            print(f"[WARN] 번역 실패 ({e}). 원문으로 검색합니다.")
            return raw_text

        if not translated:
            print("[WARN] 번역 결과 없음. 원문으로 검색합니다.")
            return raw_text

        print(f"[DEBUG] 번역된 쿼리: {translated}")
        return translated

    def recommend(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        백엔드가 호출하는 유일한 public 메서드.

        input 기대 키:
            body_part    (str): 통증 부위 (예: "knee")
            body_region  (str): 세부 위치 (예: "lateral")
            situation    (str): 상황 (예: "after_exercise")
            symptom_type (str | None): 증상 유형
            raw_text     (str): 사용자 직접 입력 텍스트
            laterality   (str): "left" | "right" | "bilateral"
        """
        # [Step 6-②] acute 입력 시 LLM 호출 없이 즉시 반환
        if input.get("acute"):
            return {"options": [], "redirect": "hospital"}

        # 1) 번역
        e_query = self._translate(input.get("raw_text", ""))

        # 2) body_part 필터로 RAG 검색
        filters = MetadataFilters(
            filters=[ExactMatchFilter(key="body_part", value=input.get("body_part", "").lower())]
        )

        # valid_codes: SearchClient로 technique_code 컬럼 직접 조회
        # → LlamaIndex는 _node_content에서 노드를 재구성하므로 n.metadata가
        #   수동 매핑 전 값을 반환함. 컬럼 직접 조회로 우회
        base_retriever = self.index.as_retriever(similarity_top_k=6, filters=filters)
        leaf_nodes = base_retriever.retrieve(e_query)
        chunk_ids = [n.node_id for n in leaf_nodes]
        search_results = self._search_client.search(
            search_text="*",
            filter=" or ".join(f"chunk_id eq '{cid}'" for cid in chunk_ids),
            select="chunk_id,technique_code",
            top=len(chunk_ids),
        )
        valid_codes = list({
            r["technique_code"]
            for r in search_results
            if r.get("technique_code")
        })
        print(f"[DEBUG] valid_codes: {valid_codes}")

        if not valid_codes:
            print("[WARN] 검색된 노드에서 technique_code를 찾을 수 없습니다.")
            return {"options": []}

        # rag_chunks: AutoMergingRetriever로 parent 병합 후 추출 (더 넓은 컨텍스트)
        retriever = self._build_retriever(filters=filters)
        nodes = retriever.retrieve(e_query)

        # 4) 프롬프트 조합 & LLM 호출
        # chunk_id를 레이블로 붙여서 LLM이 source_chunk_ids에 실제 ID를 쓸 수 있게 함
        rag_chunks = "\n\n".join(
            f"[chunk_id: {n.node_id}]\n{n.get_content()}"
            for n in nodes
        )
        prompt = RECOMMENDATION_PROMPT.format(
            valid_codes=json.dumps(valid_codes, ensure_ascii=False),
            rag_chunks=rag_chunks,
            structured_symptom=json.dumps(input, ensure_ascii=False),
        )
        print("[DEBUG] 추천 옵션 생성 중...")
        response = self.llm.complete(prompt)

        # 5) LLM 응답(문자열) → Python dict 변환
        # [Step 6-①] JSON 파싱 실패 시 ValueError로 감싸서 백엔드가 500 처리
        try:
            result = json.loads(response.text.strip())
            # result = response.text.strip()  # JSON 문자열 그대로 반환 시
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM JSON 파싱 실패: {e}\n원문: {response.text.strip()}")

        # [Step 6-④] options 키 누락 시 빈 배열 fallback
        if "options" not in result:
            result["options"] = []

        # [Step 6-③] valid_codes 외 technique_code 반환 시 해당 option 제거
        result["options"] = [
            o for o in result["options"]
            if o.get("technique_code") in valid_codes
        ]

        return result


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    rag = TapingRAGSystem()

    # 정상 케이스
    test_input = {
        "body_part": "knee",
        "body_region": "lateral",
        "situation": "after_exercise",
        "symptom_type": "outer_pain",
        "raw_text": "달리기 후 무릎 바깥쪽 통증",
        "laterality": "right",
    }

    # acute 케이스 (LLM 호출 없이 즉시 반환되는지 확인)
    # test_input = {
    #     "body_part": "knee",
    #     "raw_text": "무릎을 심하게 삐었어요 못 걷겠어요",
    #     "acute": True,
    # }

    print(f"\n[입력]\n{json.dumps(test_input, ensure_ascii=False, indent=2)}")

    result = rag.recommend(test_input)

    print("\n" + "=" * 50)
    print("최종 응답")
    print("=" * 50)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # from azure.search.documents import SearchClient
    # from azure.core.credentials import AzureKeyCredential
    # from dotenv import load_dotenv
    # import os

    # load_dotenv()

    # client = SearchClient(
    #     endpoint=os.getenv("AZURE_AI_SEARCH_ENDPOINT"),
    #     index_name="taping-guide-index-3",
    #     credential=AzureKeyCredential(os.getenv("AZURE_AI_SEARCH_KEY")),
    # )

    # results = client.search(
    #     search_text="*",
    #     filter="body_part eq 'knee'",
    #     select="chunk_id,technique_code,body_region",
    #     top=20,
    # )

    # for r in results:
    #     print(r["chunk_id"][:8], r.get("technique_code"), r.get("body_region"))
