from pydantic import BaseModel
from typing import List

class StructuredSymptom(BaseModel):
    area: str
    keywords: List[str]
    summary: str

class SymptomResponse(BaseModel):
    session_id: str
    status: str
    structured_symptom: StructuredSymptom # 임시 message 필드 삭제 및 구조화