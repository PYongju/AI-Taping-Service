from fastapi import APIRouter, HTTPException
import uuid
from datetime import datetime
# 절대 경로로 스키마 불러오기
from app.schemas.symptoms import SymptomRequest, SymptomResponse

symptom_router = APIRouter()

@symptom_router.post("/analyze", response_model=SymptomResponse)
async def analyze_symptoms(request: SymptomRequest):
    try:
        # 임시 세션 ID 생성
        new_session_id = f"sess_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
        
        print(f"[LOG] 프론트엔드 요청 수신: {request.body_part}, {request.raw_text}")
        print(f"[LOG] 생성된 세션 ID: {new_session_id}")
        
        return SymptomResponse(
            session_id=new_session_id,
            status="SCENE_1_COMPLETED",
            message="증상 데이터 수신 및 세션 생성이 완료되었습니다."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 생성 중 오류 발생: {str(e)}")