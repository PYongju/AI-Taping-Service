import os
from pathlib import Path
from azure.storage.blob import BlobServiceClient

# 현재 feat_cv 폴더의 절대 경로
CV_BASE = Path(__file__).parent

def download_azure_resources():
    print("[LOG] CV 리소스 로컬 캐싱을 시작합니다...")
    
    # .env에서 스토리지 연결 문자열 가져오기
    connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connect_str:
        print("[WARNING] AZURE_STORAGE_CONNECTION_STRING이 없어 로컬 파일을 사용합니다.")
        return

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client("models")

    # 1. MediaPipe Task 파일 다운로드
    task_path = CV_BASE / "pose_landmarker_full.task"
    if not task_path.exists():
        print(" -> pose_landmarker_full.task 다운로드 중...")
        with open(task_path, "wb") as f:
            f.write(container_client.get_blob_client("pose_landmarker_full.task").download_blob().readall())

    # 2. Body JSON 폴더 동기화
    json_dir = CV_BASE / "body_jsons"
    json_dir.mkdir(exist_ok=True)
    
    # 스토리지의 body_json/ 폴더 내성 탐색
    blob_list = container_client.list_blobs(name_starts_with="body_json/")
    for blob in blob_list:
        file_name = blob.name.split("/")[-1] # 파일명만 추출
        if not file_name: continue
        
        local_file_path = json_dir / file_name
        if not local_file_path.exists():
            print(f" -> {file_name} 다운로드 중...")
            with open(local_file_path, "wb") as f:
                f.write(container_client.get_blob_client(blob.name).download_blob().readall())

    print("[SUCCESS] CV 필수 리소스 로컬 캐싱 완료!")

if __name__ == "__main__":
    download_azure_resources()