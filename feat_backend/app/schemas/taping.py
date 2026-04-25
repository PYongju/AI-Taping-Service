from pydantic import BaseModel
from typing import List, Optional

class TapingRequest(BaseModel):
    session_id: str

class TapingStep(BaseModel):
    step: int
    title: str
    instruction: str
    # 🌟 기본값을 설정하여 LLM 데이터가 없어도 화면이 비지 않게 합니다.
    pose: Optional[str] = "편안한 자세를 취하고 안내를 따라주세요."
    warn: Optional[str] = "통증이 느껴지면 즉시 중단하세요."

class TapingOption(BaseModel):
    option_rank: int
    technique_code: str
    title: Optional[str] = "추천 테이핑"
    name: Optional[str] = "추천 테이핑"
    why: Optional[str] = "분석된 추천 사유입니다."
    coach: Optional[str] = "안내에 따라 진행해주세요."
    model_url: Optional[str] = None
    video_url: Optional[str] = None
    stretch_pct: Optional[int] = 0
    steps: List[TapingStep] = []

class TapingResponse(BaseModel):
    session_id: str
    status: str
    analysis: str
    options: List[TapingOption]

# 🌟 챗봇 대화를 위한 새로운 설계도
class ChatRequest(BaseModel):
    session_id: str
    current_step: int
    instruction: str
    message: str