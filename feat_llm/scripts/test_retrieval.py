import os
import sys
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.azureaisearch import AzureAISearchVectorStore, MetadataIndexFieldType
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.storage.docstore import SimpleDocumentStore

# 1. 이전에 만든 임베딩/LLM 설정 모듈 임포트
from resource_config import setup_global_llm_and_embedding

sys.stdout.reconfigure(encoding='utf-8')

def test_search_quality(index_name: str, query: str, filter_body_part: str = None):
    """
    Azure AI Search 인덱스에 직접 쿼리를 날려 검색된 청크의 질을 평가합니다.
    """
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
    
    # 전역 임베딩 모델 세팅 (text-embedding-3-small 적용)
    setup_global_llm_and_embedding()

    print(f"\n[1] '{index_name}' 인덱스에 연결 중...")
    
    search_client = SearchIndexClient(
        endpoint=os.getenv("AZURE_AI_SEARCH_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("AZURE_AI_SEARCH_KEY"))
    )

    # 2. 벡터 스토어 연결 (업로드할 때와 동일한 스키마 키 매핑 필수)
    vector_store = AzureAISearchVectorStore(
        search_or_index_client=search_client,
        index_name=index_name,
        
        # 1. 필수 키 매핑 (Azure Portal 실제 이름 기준)
        id_field_key="chunk_id",
        chunk_field_key="chunk",
        embedding_field_key="text_vector",
        doc_id_field_key="parent_id",
        metadata_string_field_key="metadata",
        filterable_metadata_field_keys={
            "source": ("source", MetadataIndexFieldType.STRING),
            "body_part": ("body_part", MetadataIndexFieldType.STRING),
            "technique_code": ("technique_code", MetadataIndexFieldType.STRING),
            "condition": ("condition", MetadataIndexFieldType.STRING),
            "region": ("region", MetadataIndexFieldType.STRING),
            "min_stretch": ("min_stretch", MetadataIndexFieldType.INT32),
            "max_stretch": ("max_stretch", MetadataIndexFieldType.INT32),
        },
        # 2. 모든 메타데이터를 개별 필드로 밖으로 빼기
        metadata_column_container={
            "source": "source",
            "body_part": "body_part",
            "technique_code": "technique_code",
            "region": "region",
            "condition": "condition",
            "min_stretch": "min_stretch",
            "max_stretch": "max_stretch",
            "contraindication": "contraindication",
            # "condition_aliases": "condition_aliases" 
        }
    )

    # 3. 인덱스 로드 (업로드된 데이터와 연결)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # 4. 메타데이터 필터 설정 (옵션)
    filters = None
    if filter_body_part:
        clean_body_part = filter_body_part.strip().lower()
        filters = MetadataFilters(
            filters=[ExactMatchFilter(key="body_part", value=clean_body_part)]
        )
        print(f"[2] 🎯 필터 적용됨: body_part == '{filter_body_part}'")

    print(f"[3] 🔍 질문 검색 중: '{query}'\n")
    
    # 5. 리트리버 생성 및 검색 실행 (상위 3개 추출)
    retriever = index.as_retriever(similarity_top_k=3, filters=filters)
    nodes = retriever.retrieve(query)

    # 6. 결과 출력 (디버깅)
    print("="*50)
    print("검색 결과 (Top 3)")
    print("="*50)
    
    if not nodes:
        print("검색된 데이터가 없습니다.")
        return

    for i, node in enumerate(nodes, 1):
        # LlamaIndex에서 반환된 Node 객체의 메타데이터와 텍스트를 확인
        meta = node.metadata
        print(f"\n[{i}순위] 유사도 점수(Score): {node.score:.4f}")
        print(f" 📍 ID: {meta.get('id', 'N/A')}")
        print(f" 📍 부위/질환: {meta.get('body_part')} / {meta.get('condition')}")
        print(f" 📝 원문 미리보기:\n   {node.text[:200]}...")

if __name__ == "__main__":
    TARGET_INDEX = "taping-guide-index2" 
    
    # 테스트 1: 필터 없이 순수 벡터 검색만 테스트
    TEST_QUERY_1 = "Lateral knee pain taping steps"
    test_search_quality(TARGET_INDEX, TEST_QUERY_1)
    
    # 테스트 2: 'knee' 부위로 필터링을 걸고 하이브리드 검색 테스트
    test_search_quality(TARGET_INDEX, TEST_QUERY_1, filter_body_part="knee")