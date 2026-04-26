import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding='utf-8')

from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.vector_stores.azureaisearch import AzureAISearchVectorStore,IndexManagement
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

RECOMMENDATION_PROMPT = """
## Role
You are a taping guidance system that suggests self-care options based on patterns, not a medical expert.
You will receive (1) a structured symptom, and (2) retrieved textbook passages. 
Your job is to recommend taping options and explain WHY each option helps based on the provided data.

## Guidelines
- Output ONLY valid JSON. No explanation, no markdown.
- You MUST only recommend taping_ids from the VALID SET provided below.
- Do NOT invent techniques outside this list.
- If no technique in the valid set matches, return an empty options array.
- All "why" fields must be grounded in the retrieved passages. If a passage does not support a claim, do not make the claim.
- "why" must explain the effect in simple, functional terms the user can understand.
- Avoid anatomical explanations; focus on sensation or support (e.g., "바깥쪽 부담을 줄이는 데 도움").
- coaching_text must follow:
  1 what to do (추천 행동)
  2 why it helps (간단 이유)
- "analysis" should describe the situation, NOT interpret or diagnose.
- Avoid causal or medical conclusions.

## Tone and Language Guidelines
To ensure user safety and regulatory compliance, please apply these rules to ALL output fields ("why", "coaching_text", "disclaimer", "name_ko"):
- Do NOT expose internal medical/anatomical terms directly (e.g., IT band, patella).
- Always translate them into user-friendly expressions (e.g., "무릎 바깥쪽", "무릎 앞쪽").
- **Use supportive, non-clinical language:** Avoid medical jargon like "diagnose," "treat," or "prescribe."
- **Frame as Wellness Guidance:** All recommendations must be framed as general self-care or wellness guidance, not as professional medical advice.
- **Use Possibility Expressions:** Prefer phrases like "~에 도움이 될 수 있어요", "~관리에 도움이 돼요", or "~할 가능성이 있어요" over absolute statements.
- **Avoid Definitive Claims:** Do not use words like "perfect match," "best solution," or "guaranteed outcome." Instead, use "commonly used," "frequently applied," or "suitable for your body type."
- **Service Responsibility:** Instead of phrases like "사용자 책임입니다", use gentle guidance like "이 서비스는 예방적 셀프케어를 위한 가이드입니다. 증상이 지속되면 전문가와 상담하세요."

## Valid Technique Codes for this Request
{valid_codes}

## Retrieved Textbook Passages
{rag_chunks}

## Structured Symptom
{structured_symptom}

## Output Schema
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

## Safety Rules
- If structured_symptom contains "acute": true → return {{"options": [], "redirect": "hospital"}}
- **Mismatched Input Rule:** If the inputted `body_part` significantly contradicts the user's actual symptoms in `raw_text` or `keywords` (e.g., `body_part` is "knee" but keywords/text indicate "ankle_pain"):
   → Return `"options": []`
   → Set `"coaching_text": "선택하신 통증 부위와 질문 내용이 달라요!"`
   → Describe the user's actual situation based on raw_text/keywords in `"analysis"`.
   → Keep `"body_part"` exactly as provided in the input.
- Never mention body parts outside the structured_symptom body_part (unless addressing a mismatch as described in the rule above).
- If {rag_chunks} is empty OR contains no relevant passages:
   → coaching_text: "교본 자료가 제한적이에요. 증상이 지속되면 전문가 확인을 권해요."
   → Each option's "why": "교본 자료가 제한적이에요. 전문가 확인을 권해요."
   → Do NOT hallucinate textbook content. Only state what the passages explicitly support.
- If textbook passages are insufficient for a specific option, set that option's "why" to: "교본 자료가 제한적이에요. 전문가 확인을 권해요."
- steps: Based on the taping procedure chunks. If not found, return [].
- steps.tape_type: Actual tape type used in the step. If unknown, return null.
- source_chunk_ids: Only include the IDs of the nodes actually used.
- Output must be pure JSON only.
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
        base_retriever = self.index.as_retriever(similarity_top_k=6, filters=filters, vector_store_query_mode=VectorStoreQueryMode.HYBRID)

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
        if not raw_text or not raw_text.strip():
            return ""
        # 🌟 여기에 강력한 제약 조건을 추가했습니다.
        prompt = (
            "You are a medical translator specializing in kinesiology taping. "
            "Translate the user's Korean input into English medical terms for searching professional documents.\n"
            "CRITICAL RULE: Output ONLY the translated English terms. Do NOT include any conversational filler, greetings, or explanations like 'Of course!' or 'Here is the translation'. "
            "If you cannot translate, just output the original text.\n\n"
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
            session_id          (str): 세션 ID (llm 내부에서 사용 안 함)
            model_id            (str): 3D 모델 ID (llm 내부에서 사용 안 함)
            body_part           (str): 통증 부위 (예: "knee")
            situation           (str): 상황 (예: "after_exercise")
            laterality          (str): "left" | "right" | "bilateral"
            raw_text            (str): 사용자 직접 입력 텍스트
            structured_symptom  (dict): EP1에서 구조화된 증상 정보
                area     (str) : 세부 위치 (예: "knee_lateral")
                keywords (list): 증상 키워드 (예: ["outer_pain", "running"])
        """
        # [Step 6-②] acute 입력 시 LLM 호출 없이 즉시 반환
        if input.get("acute"):
            return {"options": [], "redirect": "hospital"}

        # 1) 번역
        # 1) 검색어(e_query) 설정 방어 로직
        # 1) 검색어(e_query) 설정 방어 및 극단적 압축
        raw_text = input.get("raw_text", "")
        if raw_text and raw_text.strip():
            e_query = self._translate(raw_text)
        else:
            structured = input.get("structured_symptom", {})
            # 노이즈를 없애기 위해 가장 핵심이 되는 부위(area) 키워드 1개만 추출
            area = structured.get("area", "").replace("_", " ")
            if not area.strip() and structured.get("keywords"):
                area = structured.get("keywords")[0]
            
            e_query = f"{area} taping".strip()
            if not e_query.strip():
                e_query = "knee taping"
                
            print(f"[DEBUG] 직접 입력 없음. 압축된 대체 검색어: {e_query}")

        # 🌟 2) body_part 필터 매핑 (핵심: 한글 '무릎' -> 영문 'knee' 변환)
        input_part = input.get("body_part", "무릎")
        part_map = {
            "무릎": "knee",
            "발목": "ankle",
            "어깨": "shoulder",
            "허리": "back",
            "팔꿈치": "elbow",
            "손목": "wrist"
        }
        db_body_part = part_map.get(input_part, "knee") # 매핑 실패 시 기본값 knee

        filters = MetadataFilters(
            filters=[ExactMatchFilter(key="body_part", value=db_body_part)]
        )

        # 3) RAG 검색 실행 (top_k=15 유지)
        base_retriever = self.index.as_retriever(similarity_top_k=15, filters=filters)
        leaf_nodes = base_retriever.retrieve(e_query)
        chunk_ids = [n.node_id for n in leaf_nodes]
        
        if not chunk_ids:
            print("[WARN] 검색된 문서가 0개입니다.")
            return {"options": []}

        search_results = self._search_client.search(
            search_text="*",
            filter=" or ".join(f"chunk_id eq '{cid}'" for cid in chunk_ids),
            select="chunk_id,technique_code",
            top=len(chunk_ids),
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
        
        # RAG가 찾아온 원본 코드들
        raw_valid_codes = list({
            r["technique_code"]
            for r in search_results
            if r.get("technique_code")
        })

        # 🌟 [수정 포인트] 영상이 준비된 4개의 코드 (화이트리스트)
        ALLOWED_CODES = {
            "KT_KNEE_MEDIAL",
            "KT_KNEE_MALALIGNMENT_ALTERNATIVE",
            "KT_KNEE_LATERAL",
            "KT_KNEE_GENERAL"
        }
        
        # 교집합 연산을 통해 영상이 있는 코드만 남기기
        valid_codes = list(set(raw_valid_codes) & ALLOWED_CODES)
        print(f"[DEBUG] 영상 필터링 적용 후 valid_codes: {valid_codes}")

        if not valid_codes:
            print("[WARN] 매칭되는 영상/코드가 없습니다.")
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
        # session_id, model_id는 LLM 프롬프트에 불필요하므로 제거 후 전달
        llm_context = {k: v for k, v in input.items() if k not in ("session_id", "model_id")}
        prompt = RECOMMENDATION_PROMPT.format(
            valid_codes=json.dumps(valid_codes, ensure_ascii=False),
            rag_chunks=rag_chunks,
            structured_symptom=json.dumps(llm_context, ensure_ascii=False),
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
    
    def chat(self, user_message: str, current_step: int, instruction: str) -> str:
        """
        테리(챗봇)가 가이드 단계와 사용자의 질문을 바탕으로 답변을 생성하는 함수입니다.
        """
        if not user_message or not user_message.strip():
            return "궁금한 점을 입력해주세요!"

        # 테리가 문맥을 이해할 수 있도록 프롬프트를 구성합니다.
        prompt = (
            "You are a friendly, helpful, and professional physical therapy assistant named 'Terry' (테리). "
            "You provide guidance on kinesiology taping based on the specific step the user is currently looking at.\n\n"
            f"Current Step: {current_step}\n"
            f"Step Instruction: {instruction}\n"
            f"User's Question: {user_message}\n\n"
            "CRITICAL RULES:\n"
            "1. Answer in natural, friendly Korean.\n"
            "2. Keep the answer concise (2-3 sentences) and easy to understand.\n"
            "3. Do NOT provide medical diagnoses. Remind the user to seek professional help if they experience severe pain.\n"
            "4. Focus your answer strictly on helping the user understand the 'Current Step' and their question."
        )

        try:
            print(f"[DEBUG] 챗봇 LLM 호출 시작... 질문: {user_message}")
            response = self.llm.complete(prompt)
            reply = response.text.strip()
            print(f"[DEBUG] 챗봇 응답 완료: {reply}")
            return reply
        except Exception as e:
            print(f"[ERROR] 챗봇 LLM 생성 실패: {e}")
            return "앗, 테리가 잠깐 생각하느라 머리가 엉켰어요. 다시 한 번 물어봐주시겠어요?"


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