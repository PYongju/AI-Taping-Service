from pydantic import BaseModel
from typing import Optional

class BodyMetrics(BaseModel):
    bmi_group: Optional[str] = None
    # 추가 필요한 metric이 있다면 여기에 추가하세요

class BodyMatchResponse(BaseModel):
    session_id: str
    status: str
    model_id: str
    glb_url: str          # 매칭된 모델의 GLB 주소
    match_type: str       # 'AI_MATCH' 또는 'DEFAULT_FALLBACK'
    body_metrics: BodyMetrics