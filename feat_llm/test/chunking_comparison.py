import os
import sys
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex, Settings
from llama_index.core.node_parser import MarkdownNodeParser, HierarchicalNodeParser, get_leaf_nodes
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

# 인코딩 설정 (이모지 및 한글 깨짐 방지)
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

# Azure OpenAI 설정
Settings.llm = AzureOpenAI(engine="gpt-4.1", api_key=os.getenv("AZURE_OPENAI_API_KEY"), azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), api_version="2024-02-15-preview")
Settings.embed_model = AzureOpenAIEmbedding(model="text-embedding-3-small", deployment_name="text-embedding-3-small", api_key=os.getenv("AZURE_OPENAI_API_KEY"), azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), api_version="2024-02-15-preview")

def compare_chunking_results(query):
    data_dir = r"feat_llm\test\data"
    
    # 1. Markdown 파싱 결과 생성
    md_docs = SimpleDirectoryReader(input_dir=data_dir, required_exts=[".md"]).load_data()
    md_nodes = MarkdownNodeParser().get_nodes_from_documents(md_docs)
    md_index = VectorStoreIndex(md_nodes)
    
    # 2. Plain Text (계층적) 파싱 결과 생성
    txt_docs = SimpleDirectoryReader(input_dir=data_dir, required_exts=[".txt"]).load_data()
    h_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[1024, 256])
    txt_all_nodes = h_parser.get_nodes_from_documents(txt_docs)
    txt_leaf_nodes = get_leaf_nodes(txt_all_nodes)
    txt_index = VectorStoreIndex(txt_leaf_nodes)

    print(f"\n" + "="*50)
    print(f"🔍 질문: {query}")
    print("="*50)

    # --- 실험 A: Markdown Retriever ---
    print("\n[실험 A] MarkdownNodeParser 결과")
    md_retriever = md_index.as_retriever(similarity_top_k=2)
    md_results = md_retriever.retrieve(query)
    for i, res in enumerate(md_results):
        print(f"\n📌 Node {i+1} (Score: {res.score:.4f})")
        print(f"내용: {res.node.get_content()[:300]}...") # 표 구조가 살아있는지 확인

    # --- 실험 B: Plain Text Retriever ---
    print("\n\n" + "-"*50)
    print("[실험 B] HierarchicalNodeParser (TXT) 결과")
    txt_retriever = txt_index.as_retriever(similarity_top_k=2)
    txt_results = txt_retriever.retrieve(query)
    for i, res in enumerate(txt_results):
        print(f"\n📌 Node {i+1} (Score: {res.score:.4f})")
        print(f"내용: {res.node.get_content()[:300]}...") # 일반 문장으로 잘렸는지 확인

if __name__ == "__main__":
    # 비교해보고 싶은 질문을 입력하세요.
    test_query = "lateral pain taping steps and stretch percentage"
    compare_chunking_results(test_query)