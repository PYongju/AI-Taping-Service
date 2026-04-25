from pydantic import BaseModel, Field
from typing import List, Optional

class TapingRequest(BaseModel):
    session_id: str

class TapingStep(BaseModel):
    step: int
    title: str
    instruction: str
    pose: Optional[str] = "기본 자세를 유지하세요."
    warn: Optional[str] = "통증 시 즉시 중단하세요."

class TapingOption(BaseModel):
    option_rank: int
    technique_code: str
    body_region: Optional[str] = None
    tape_type: Optional[str] = None
    why: Optional[str] = "분석된 추천 사유입니다."
    anchor_position: Optional[str] = None
    guide_video_url: Optional[str] = None
    combined_glb_url: Optional[str] = None
    
    # 👇👇👇 이것들이 없어서 데이터와 3D 모델이 싹 다 날아갔던 겁니다! 👇👇👇
    title: Optional[str] = "추천 테이핑"
    name: Optional[str] = "추천 테이핑"
    coach: Optional[str] = "안내에 따라 진행해주세요."
    model_url: Optional[str] = None
    video_url: Optional[str] = None
    stretch_pct: Optional[int] = 0
    step_glb_urls: List[str] = []
    disclaimer: Optional[str] = None
    registry_key: Optional[str] = None
    taping_id: Optional[str] = None
    # 👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆
    
    steps: List[TapingStep] = []

class TapingResponse(BaseModel):
    session_id: str
    status: str
    analysis: str
    options: List[TapingOption]