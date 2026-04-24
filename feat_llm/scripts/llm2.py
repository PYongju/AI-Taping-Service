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

# [진단용 코드] 인덱스 데이터 덤프
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

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
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            embed_model=Settings.embed_model
        )

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
        # 1. Few-Shot Prompting: 예시를 직접 주어 대답 방식을 강제합니다.
        prompt = (
            "당신은 의료 전문 번역가입니다. 아래의 한국어 증상을 검색용 영어 의학 키워드로만 번역하세요.\n"
            "조건: 설명이나 인삿말 없이 오직 영어 단어만 출력하세요.\n"
            f"한국어: {raw_text}\n"
            "영어:"
        )
        try:
            response = self.llm.complete(prompt)
            translated = response.text.strip()
            # "Of course", "Please" 등이 포함되면 번역 실패로 간주
            if any(x in translated.lower() for x in ["provide", "course", "sure", "translate"]):
                return raw_text
            return translated
        except:
            return raw_text

        if not translated:
            print("[WARN] 번역 결과 없음. 원문으로 검색합니다.")
            return raw_text

        print(f"[DEBUG] 번역된 쿼리: {translated}")
        return translated

    def recommend(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        백엔드가 호출하는 유일한 public 메서드.
        """
        # [Step 6-②] acute 입력 시 LLM 호출 없이 즉시 반환
        if input.get("acute"):
            return {"options": [], "redirect": "hospital"}

        # 1) 번역 및 쿼리 확보
        raw_text = input.get("raw_text", "")
        e_query = self._translate(raw_text)

        if Settings.embed_model is None:
            print("[FATAL] Settings.embed_model이 None입니다! resource_config.py를 확인하세요.")

        # 2) body_part 필터 설정
        body_part_val = input.get("body_part", "").strip().lower()
        filters = MetadataFilters(
            filters=[ExactMatchFilter(key="body_part", value=body_part_val)]
        )

        leaf_nodes = []
        # 🌟 핵심 개선 1: Embedding 누락 등으로 인한 500 에러 원천 차단 (try-except)
        try:
            # 검색 범위 확장 (6 -> 15)
            base_retriever = self.index.as_retriever(similarity_top_k=15, filters=filters)
            leaf_nodes = base_retriever.retrieve(e_query)

            # 🌟 핵심 개선 2: 필터 검색 결과가 없으면 필터 없이 전체 검색 (Fallback)
            if not leaf_nodes:
                print("[INFO] 필터 검색 결과 없음. 필터 없이 재검색 시도")
                base_retriever = self.index.as_retriever(similarity_top_k=15)
                leaf_nodes = base_retriever.retrieve(e_query)
                
                # 그래도 없으면 한글 원문(raw_text)으로 마지막 검색 시도
                if not leaf_nodes:
                    print("[INFO] 번역 쿼리 검색 결과 없음. 원문으로 재검색 시도")
                    leaf_nodes = base_retriever.retrieve(raw_text)

        except Exception as e:
            print(f"[ERROR] 검색 중 에러 발생 (Embedding 오류 등): {e}")
            # 서버가 죽지 않고 프론트엔드로 안전하게 에러 메시지 전달
            return {"options": [], "coaching_text": "검색 엔진 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}

        # 3) Technique Code 추출
        chunk_ids = [n.node_id for n in leaf_nodes if n.node_id]
        valid_codes = []

        # 🌟 핵심 개선 3: chunk_ids가 비어있을 때 Azure Search를 호출하면 터지는 버그 방지
        if chunk_ids:
            try:
                search_results = self._search_client.search(
                    search_text="*",
                    filter=" or ".join(f"chunk_id eq '{cid}'" for cid in chunk_ids),
                    select="chunk_id,technique_code",
                    top=len(chunk_ids),
                )
                for r in search_results:
                    code = r.get("technique_code")
                    if code:
                        valid_codes.append(code)
                
                # 중복 코드 제거
                valid_codes = list(set(valid_codes))
            except Exception as e:
                print(f"[ERROR] Azure Search 메타데이터 조회 중 에러: {e}")

        print(f"[DEBUG] 최종 추출된 valid_codes: {valid_codes}")

        # 🌟 핵심 개선 4: valid_codes가 없어도 뻗지 않고 안내 멘트(coaching_text)와 함께 안전하게 반환
        if not valid_codes:
            print("[WARN] 검색된 노드에서 technique_code를 찾을 수 없습니다.")
            return {
                "options": [],
                "coaching_text": "해당 증상에 맞는 정확한 테이핑 기법을 찾지 못했어요. 통증이 심하다면 전문가의 진료를 권장합니다."
            }

        # rag_chunks: AutoMergingRetriever로 parent 병합 후 추출
        current_filters = filters if len(leaf_nodes) > 0 else None
        retriever = self._build_retriever(filters=current_filters)
        try:
            nodes = retriever.retrieve(e_query)
        except Exception:
            nodes = leaf_nodes # 에러 시 기존에 찾은 노드 재사용

        # 4) 프롬프트 조합 & LLM 호출
        rag_chunks = "\n\n".join(
            f"[chunk_id: {n.node_id}]\n{n.get_content()}"
            for n in nodes
        )
        llm_context = {k: v for k, v in input.items() if k not in ("session_id", "model_id")}
        prompt = RECOMMENDATION_PROMPT.format(
            valid_codes=json.dumps(valid_codes, ensure_ascii=False),
            rag_chunks=rag_chunks,
            structured_symptom=json.dumps(llm_context, ensure_ascii=False),
        )
        
        print("[DEBUG] 추천 옵션 생성 중...")
        try:
            response = self.llm.complete(prompt)
        except Exception as e:
            print(f"[ERROR] LLM 답변 생성 중 에러: {e}")
            return {"options": [], "coaching_text": "AI 분석 중 오류가 발생했습니다."}

        # 5) LLM 응답(문자열) → Python dict 변환
        try:
            result = json.loads(response.text.strip())
        except json.JSONDecodeError as e:
            print(f"[ERROR] LLM JSON 파싱 실패: {e}\n원문: {response.text.strip()}")
            # 🌟 핵심 개선 5: JSON 파싱에 실패해도 500 에러 대신 안전하게 종료
            return {"options": [], "coaching_text": "추천 결과를 분석하는 중 문제가 발생했습니다."}

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
        "session_id": "sess_abc123",
        "model_id": "M0234",
        "body_part": "knee",
        "situation": "after_exercise",
        "laterality": "right",
        "raw_text": "달리기 후 무릎 바깥쪽 통증",
        "structured_symptom": {
            "area": "knee_lateral",
            "keywords": ["outer_pain", "running"],
        },
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

    # 환경변수가 로드되어 있다는 가정하에 실행
    client = SearchClient(
        endpoint=os.getenv("AZURE_AI_SEARCH_ENDPOINT"),
        index_name="taping-guide-index-3", # 사용 중인 인덱스 이름
        credential=AzureKeyCredential(os.getenv("AZURE_AI_SEARCH_KEY")),
    )

    print("\n--- 인덱스 데이터 샘플링 시작 ---")
    results = client.search(search_text="*", select="chunk_id,body_part,technique_code", top=10)
    for r in results:
        print(f"ID: {r['chunk_id'][:10]} | Body: {r.get('body_part')} | Code: {r.get('technique_code')}")
    print("--- 샘플링 끝 ---\n")

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
