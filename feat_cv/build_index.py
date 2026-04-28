# build_index.py
import os
import json
from pathlib import Path
from azure.storage.blob import BlobServiceClient
from cv import compute_body_features_from_points
from dotenv import load_dotenv

# 💡 [핵심 수정] 옆 동네(feat_backend)에 있는 .env 파일의 정확한 경로를 찾습니다.
# 현재 파일(feat_cv)의 부모 폴더로 간 뒤 -> feat_backend -> .env 를 가리킴
env_path = Path(__file__).resolve().parent.parent / "feat_backend" / ".env"
load_dotenv(dotenv_path=env_path)

# 이제 파이썬이 정확한 .env를 찾아서 값을 가져옵니다!
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "models"

def build_and_upload_index():
    print("🚀 통합 인덱스 파일 생성을 시작합니다. (시간이 조금 걸립니다!)")
    
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    blob_list = container_client.list_blobs(name_starts_with="body_json/")
    all_models_index = []

    count = 0
    for blob in blob_list:
        try:
            # 1. 파일 다운로드 및 파싱
            blob_client = container_client.get_blob_client(blob)
            data_stream = blob_client.download_blob().readall()
            raw_data = json.loads(data_stream)
            
            # 2. 비율 계산 (핵심!)
            keypoint_dict = {kp["name"]: [kp["x"], kp["y"], kp["z"]] for kp in raw_data["keypoints"]}
            pts_xy = {k: [v[0], v[1]] for k, v in keypoint_dict.items()}
            _, ratios = compute_body_features_from_points(pts_xy)
            
            actor = raw_data.get("actor", {})
            mesh = raw_data.get("mesh", {})
            annotation = raw_data.get("annotation", {})
            
            # 3. 엑기스(알맹이)만 뽑아서 딕셔너리 생성
            info = {
                "json_path": blob.name,
                "annotation_id": annotation.get("id"),
                "model_id": mesh.get("mesh_id", blob.name),
                "sex": actor.get("sex"),
                "actor_height_cm": actor.get("height"),
                "actor_weight_kg": actor.get("weight"),
                "mesh_obj_file_name": mesh.get("obj_file_name"),
                "ratio_features": ratios, # 미리 계산된 비율 저장!
            }
            all_models_index.append(info)
            count += 1
            
            if count % 100 == 0:
                print(f"✅ {count}개 모델 처리 완료...")
                
        except Exception as e:
            print(f"[SKIP] {blob.name}: {e}")

    print(f"🎉 총 {len(all_models_index)}개의 모델 인덱싱 완료! Azure에 업로드합니다...")

    # 4. 완성된 리스트를 단일 JSON 파일로 Azure에 바로 업로드
    index_json_str = json.dumps(all_models_index, ensure_ascii=False)
    index_blob_client = container_client.get_blob_client("all_models_index.json")
    index_blob_client.upload_blob(index_json_str, overwrite=True)
    
    print("🚀 'all_models_index.json' 업로드 완벽 성공!")

if __name__ == "__main__":
    build_and_upload_index()