# feat_cv/url_utils.py
STORAGE_BASE_URL = "https://{YOUR_STORAGE_ACCOUNT}.blob.core.windows.net/models"

def get_model_url(model_id: str, is_taped: bool = False, part: str = "KNEE") -> str:
    if is_taped:
        # 무릎 테이핑 모델: knee/3148M_KT_KNEE_GENERAL.glb
        blob_path = f"knee/{model_id}_KT_{part}_GENERAL.glb"
    else:
        # 일반 바디 모델: body/3001M_BD_B.glb
        blob_path = f"body/{model_id}_BD_B.glb"
    
    return f"{STORAGE_BASE_URL}/{blob_path}"