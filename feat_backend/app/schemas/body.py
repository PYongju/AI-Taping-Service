from pydantic import BaseModel
from typing import Optional

class BodyMatchResponse(BaseModel):
    session_id: str
    status: str
    model_id: str
    glb_url: str
    match_type: str
    # metrics는 향후 MediaPipe에서 추출된 체형 비율 수치를 담기 위함
    metrics: Optional[dict] = None