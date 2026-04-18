import os
import sys
import json
import re
from typing import Dict, Any
from llama_index.core import VectorStoreIndex, PromptTemplate, Settings
from llama_index.vector_stores.azureaisearch import AzureAISearchVectorStore
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from resource_config import setup_global_llm_and_embedding

sys.stdout.reconfigure(encoding='utf-8')

class TapingRAGSystem:
    def __init__(self, index_name: str):
        # 1. 글로벌 LLM 및 임베딩 설정 (가장 먼저 실행)
        setup_global_llm_and_embedding()
        
        self.index_name = index_name
        # 2. 설정된 LLM 가져오기 (NameError 방지)
        self.llm = Settings.llm 
        
        # 3. 쿼리 엔진 초기화
        self._setup_query_engine()

    def translate_to_english(self, k_query: str) -> str:
        """한국어 질문을 영어로 번역하여 검색 품질 향상"""
        prompt = (
            "You are a medical translator specializing in kinesiology taping. "
            "Translate the user's Korean question into English medical terms for searching professional documents.\n\n"
            f"Korean: {k_query}\nEnglish:"
        )
        # Settings.llm의 complete 함수를 사용해 간편하게 요청
        response = self.llm.complete(prompt)
        translated_query = response.text.strip()
        print(f"[DEBUG] 번역된 쿼리: {translated_query}")
        return translated_query

    def _setup_query_engine(self):
        """Azure AI Search VectorStore 및 인덱스 연결"""
        search_client = SearchIndexClient(
            endpoint=os.getenv("AZURE_AI_SEARCH_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("AZURE_AI_SEARCH_KEY")) 
        )

        vector_store = AzureAISearchVectorStore(
            search_or_index_client=search_client,
            index_name=self.index_name,
            id_field_key="chunk_id",
            chunk_field_key="chunk",
            embedding_field_key="text_vector",
            doc_id_field_key="parent_id",
            metadata_string_field_key="metadata",
            filterable_metadata_field_keys=["source", "body_part", "technique_code", "condition", "region"]
        )
        self.index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    def get_structured_response(self, k_query: str, filter_body_part: str = None) -> Dict[str, Any]:
        """번역 -> RAG 검색 -> JSON 포맷팅의 전체 파이프라인"""
        # 1. 번역 진행
        e_query = self.translate_to_english(k_query)

        # 2. 메타데이터 필터 (옵션)
        filters = None
        if filter_body_part:
            filters = MetadataFilters(
                filters=[ExactMatchFilter(key="body_part", value=filter_body_part.strip().lower())]
            )

        # 3. JSON 출력을 강제하는 프롬프트 (중괄호 이중 처리 {{ }} 로 LlamaIndex 에러 방지)
        json_prompt_tmpl = PromptTemplate(
            "당신은 키네시올로지 테이핑 전문가입니다. 아래 제공된 [Context] 정보를 바탕으로 질문에 답하세요.\n"
            "답변은 반드시 아래의 JSON 형식을 엄격히 지켜서 작성해야 합니다.\n"
            "만약 정보가 부족하다면 \"N/A\" 또는 빈 리스트로 채우세요.\n\n"
            "[JSON Format]\n"
            "{{\n"
            "  \"id\": \"문서 고유 ID\",\n"
            "  \"source\": \"출처 정보\",\n"
            "  \"body_part\": \"신체 부위\",\n"
            "  \"technique_code\": \"기법 코드\",\n"
            "  \"region\": \"세부 부위\",\n"
            "  \"condition\": \"질환명\",\n"
            "  \"condition_aliases\": [\"별칭1\", \"별칭2\"],\n"
            "  \"stretch_pct_range\": [최소값, 최대값],\n"
            "  \"contraindication\": \"금기사항\",\n"
            "  \"test\": \"문서를 바탕으로 전체 테이핑 단계(Step 1, 2...), 환자의 준비 자세(Position), 테이프의 텐션(Stretch %)을 모두 포함하여 아주 상세한 줄글 가이드를 작성하세요. 문단 구분을 위해 반드시 '\\n' 기호를 사용하세요.\"\n"
            "}}\n\n"
            "[Context]\n"
            "{context_str}\n\n"
            "질문: {query_str}\n"
            "답변 (오직 JSON만 출력하세요):"
        )

        # 4. 쿼리 엔진 생성 (Top 1 문서만 참고)
        query_engine = self.index.as_query_engine(
            similarity_top_k=1, 
            filters=filters,
            response_mode="compact"
        )
        # 프롬프트 업데이트
        query_engine.update_prompts({"response_synthesizer:text_qa_template": json_prompt_tmpl})
        
        print("[DEBUG] AI가 문서를 분석하여 JSON 응답을 생성하는 중...")
        raw_response = query_engine.query(e_query)
        
        # 5. 응답에서 순수 JSON만 추출 (정규식 사용)
        try:
            json_str = re.search(r'\{.*\}', str(raw_response), re.DOTALL).group()
            return json.loads(json_str)
        except Exception as e:
            print(f"[ERROR] JSON 파싱에 실패했습니다. LLM의 원본 응답을 확인하세요.\n{raw_response}")
            return {"error": "JSON Parsing Failed", "raw": str(raw_response)}

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv() # 환경 변수 로드
    
    # 클래스 인스턴스화
    rag = TapingRAGSystem(index_name="taping-guide-index")
    
    # 실행 테스트
    test_question = "무릎 바깥쪽 통증(IT 밴드 마찰 증후군) 테이핑 방법 알려줘"
    print(f"\n[질문] {test_question}")
    
    result = rag.get_structured_response(test_question, filter_body_part="knee")
    
    print("\n" + "="*50)
    print("최종 생성된 JSON 구조")
    print("="*50)
    print(json.dumps(result, indent=2, ensure_ascii=False))