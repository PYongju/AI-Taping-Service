from fastapi import APIRouter, HTTPException
import uuid
from datetime import datetime, timezone
from app.schemas.symptoms import SymptomRequest, SymptomResponse, StructuredSymptom

# 방금 만든 db 매니저를 불러옵니다!
from app.services.db_manager import db 

symptom_router = APIRouter()

@symptom_router.post("/analyze", response_model=SymptomResponse)
async def analyze_symptoms(request: SymptomRequest):
    try:
        new_session_id = f"sess_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
        now_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # 1. Cosmos DB에 넣을 세션 데이터(JSON) 구조 만들기 (필수 키 포함)
        session_document = {
            "id": new_session_id,                 # [추가] 필수 문서 고유 ID
            "session_id": new_session_id,         # [추가] 필수 파티션 키
            "status": "SCENE_2_COMPLETED",        # 진행 상태 통일
            "created_at": now_time,               # [추가] 생성 시간
            "updated_at": now_time,               # [추가] 업데이트 시간
            "user_input": {                       # 스펙에 맞춘 통합 구조
                "body_part": request.body_part,
                "situation": request.situation,
                "raw_text": request.raw_text,
                "physical_info": {         
                    "height_cm": request.height_cm,
                    "weight_kg": request.weight_kg,
                    "gender": request.gender
                }
            }
        }
    
        # 2. 진짜로 DB에 밀어 넣기! (변수명 통일)
        db.create_session(session_document)
        print(f"[LOG] DB 저장 완료. Session: {new_session_id}")
        
        # 3. 임시(Mock) 구조화된 증상 데이터 생성
        # 실제로는 여기서 LLM(RAG)이 raw_text를 분석해서 아래 결과를 만들어야 합니다.
        mock_structured_symptom = StructuredSymptom(
            area=request.body_part,
            keywords=[request.situation, "통증"],
            summary="입력된 증상을 바탕으로 분석을 시작합니다."
        )

        # 4. 방금 정정한 스키마에 맞춘 반환
        return SymptomResponse(
            session_id=new_session_id,
            status="SCENE_2_COMPLETED",           # 상태값 통일
            structured_symptom=mock_structured_symptom  # message 대신 구조화된 객체 반환
        )

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"DB 저장 중 오류 발생: {str(e)}")