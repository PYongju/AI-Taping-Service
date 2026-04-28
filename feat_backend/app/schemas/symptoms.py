from pydantic import BaseModel, Field
from typing import List, Optional

# 1. LLM이 분석한 구조화된 증상 데이터 스키마
class StructuredSymptom(BaseModel):
    area: str = Field(..., description="분석된 핵심 부위 (예: knee_lateral)")
    keywords: List[str] = Field(..., description="추출된 증상 키워드 리스트")
    summary: str = Field(..., description="증상에 대한 한 줄 요약")

# 2. 프론트엔드에서 API 요청 시 보내는 데이터 스키마 (EP1)
class SymptomRequest(BaseModel):
    body_part: str = Field(..., example="knee")
    situation: str = Field(..., example="running")
    raw_text: str = Field(..., example="달리기 후 무릎 바깥쪽 통증")
    symptom_type: Optional[str] = Field(None, description="Quick Reply 선택 시 들어오는 Enum 값")
    
    # 필수 필드였던 신체 정보를 선택사항으로 변경
    height_cm: Optional[float] = Field(None, example=175.0)
    weight_kg: Optional[float] = Field(None, example=70.0)
    gender: Optional[str] = Field(None, example="male")

# 3. API 요청 성공 시 프론트엔드로 반환하는 응답 스키마 (EP1)
class SymptomResponse(BaseModel):
    session_id: str = Field(..., description="생성된 고유 세션 ID")
    status: str = Field(..., example="SYMPTOMS_ANALYZED")
    structured_symptom: StructuredSymptom