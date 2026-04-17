import os
import sys
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.core.node_parser import MarkdownNodeParser, HierarchicalNodeParser, get_leaf_nodes
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

# 출력 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

# Azure OpenAI 설정
Settings.llm = AzureOpenAI(
    engine="gpt-4.1", 
    api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
    api_version="2024-02-15-preview"
)
Settings.embed_model = AzureOpenAIEmbedding(
    model="text-embedding-3-small", 
    deployment_name="text-embedding-3-small", 
    api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
    api_version="2024-02-15-preview"
)

def compare_final_responses(user_query):
    data_dir = r"feat_llm\test\data"
    
    # --- 1. MD 기반 인덱스 및 엔진 생성 ---
    md_docs = SimpleDirectoryReader(input_dir=data_dir, required_exts=[".md"]).load_data()
    md_nodes = MarkdownNodeParser().get_nodes_from_documents(md_docs)
    md_index = VectorStoreIndex(md_nodes)
    md_engine = md_index.as_query_engine(similarity_top_k=2)
    
    # --- 2. TXT 기반 인덱스 및 엔진 생성 ---
    txt_docs = SimpleDirectoryReader(input_dir=data_dir, required_exts=[".txt"]).load_data()
    h_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[1024, 256])
    txt_all_nodes = h_parser.get_nodes_from_documents(txt_docs)
    txt_leaf_nodes = get_leaf_nodes(txt_all_nodes)
    txt_index = VectorStoreIndex(txt_leaf_nodes)
    txt_engine = txt_index.as_query_engine(similarity_top_k=2)

    print("\n" + "="*80)
    print(f"🤔 질문: {user_query}")
    print("="*80)

    # --- 실험 A 결과 출력 ---
    print("\n[방법 A: Markdown 기반 답변]")
    md_response = md_engine.query(user_query)
    print(f"💬 GPT 답변:\n{md_response}")
    print("\n📍 참고한 노드 수:", len(md_response.source_nodes))

    print("\n" + "-"*80)

    # --- 실험 B 결과 출력 ---
    print("\n[방법 B: Plain Text(계층적 청킹) 기반 답변]")
    txt_response = txt_engine.query(user_query)
    print(f"💬 GPT 답변:\n{txt_response}")
    print("\n📍 참고한 노드 수:", len(txt_response.source_nodes))

if __name__ == "__main__":
    # 구체적인 수치나 단계를 요구하는 질문일수록 차이가 명확히 드러납니다.
    query = "Lateral knee pain taping steps and specific stretch percentages for each step"
    compare_final_responses(query)