from pydantic import BaseModel
from typing import Optional

class BodyMetrics(BaseModel):
    bmi_group: Optional[str] = None
    # CV 디버깅용 Raw 데이터(shoulder_width 등)는 응답 모델에서 제외

class BodyMatchResponse(BaseModel):
    session_id: str
    status: str
    model_id: str
    glb_url: str            # base_glb_url -> glb_url 로 정정
    match_type: str
    body_metrics: BodyMetrics # metrics -> body_metrics 로 정정