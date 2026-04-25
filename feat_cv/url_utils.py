# 🌟 실제 스토리지 계정명 반영 및 경로 통일
STORAGE_BASE_URL = "https://tapingdata1.blob.core.windows.net/models"

def get_model_url(model_id: str, is_taped: bool = False, part: str = "KNEE") -> str:
    """
    model_id: 3001M_BD_B 와 같은 형태 또는 JerryPing
    """
    if not model_id:
        return f"{STORAGE_BASE_URL}/body_privacy/JerryPing_BODY.glb"

    if is_taped:
        # 테이핑 모델 경로 (예: knee/3148M_KT_KNEE_GENERAL.glb)
        # model_id에서 _BD_B를 떼고 접두사만 추출 (3148M)
        base_id = model_id.split('_')[0]
        blob_path = f"{part.lower()}/{base_id}_KT_{part.upper()}_GENERAL.glb"
    else:
        # 🌟 수정한 부분: ID가 이미 _BD_B를 포함하고 있으므로 중복 추가 방지
        if "_BD_B" in model_id or "BODY" in model_id:
            blob_path = f"body_privacy/{model_id}.glb"
        else:
            blob_path = f"body_privacy/{model_id}_BD_B.glb"
    
    return f"{STORAGE_BASE_URL}/{blob_path}"

# feat_cv/url_utils.py 수정
def format_model_id(raw_id: str) -> str:
    """3148M_BD_B 형태에서 순수 ID인 3148M만 깔끔하게 추출합니다."""
    return raw_id.split('_')[0]

def build_model_url(model_id: str, is_body: bool = True) -> str:
    """폴더 규칙과 ID 규칙을 하나로 합친 공식 URL 생성기"""
    base_id = format_model_id(model_id)
    if is_body:
        folder = "body_privacy" if "JerryPing" in base_id else "body"
        filename = f"{base_id}_BD_B.glb" if "JerryPing" not in base_id else "JerryPing_BODY.glb"
    else:
        folder = "knee"
        filename = f"{base_id}_KT_KNEE_GENERAL.glb" # 예시 규칙
        
    return f"https://tapingdata1.blob.core.windows.net/models/{folder}/{filename}"