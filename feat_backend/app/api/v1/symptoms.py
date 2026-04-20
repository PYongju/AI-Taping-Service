from fastapi import APIRouter, HTTPException
import uuid
from datetime import datetime, timezone
from app.schemas.symptoms import SymptomRequest, SymptomResponse, StructuredSymptom
from app.services.db_manager import db 

symptom_router = APIRouter()

@symptom_router.post("/analyze", response_model=SymptomResponse)
async def analyze_symptoms(request: SymptomRequest):
    try:
        new_session_id = f"sess_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
        now_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # 1. 구조화된 증상 데이터 생성 (LLM 분석 단계 가정)
        # [QA-16 조치] EP3에서 재연산(GPT 중복 호출)을 방지하기 위해 
        # 응답 반환 전, 세션 생성 시점에 데이터를 먼저 완성합니다.
        mock_structured_symptom = StructuredSymptom(
            area=request.body_part,
            keywords=[request.situation, "통증"],
            summary=f"{request.body_part} 부위의 {request.situation} 상황에 대한 분석 결과입니다."
        )

        # 2. Cosmos DB 세션 문서 생성
        session_document = {
            "id": new_session_id,                 
            "session_id": new_session_id,         
            "status": "SYMPTOMS_ANALYZED",        # 의미론적 상태값 사용 권장
            "created_at": now_time,               
            "updated_at": now_time,               
            "user_input": {                       
                "body_part": request.body_part,
                "situation": request.situation,
                "raw_text": request.raw_text,
                "physical_info": {         
                    "height_cm": request.height_cm,
                    "weight_kg": request.weight_kg,
                    "gender": request.gender
                }
            },
            # [QA-16 조치] 분석된 결과를 DB에 박아둡니다.
            # model_dump()를 사용하여 Pydantic 모델을 JSON 직렬화 가능한 딕셔너리로 변환합니다.
            "structured_symptom": mock_structured_symptom.model_dump()
        }
    
        # 3. DB 저장 실행
        db.create_session(session_document)
        print(f"[LOG] DB 저장 완료. Session: {new_session_id}")
        
        # 4. 정정한 스키마에 맞춘 결과 반환
        return SymptomResponse(
            session_id=new_session_id,
            status="SYMPTOMS_ANALYZED",
            structured_symptom=mock_structured_symptom
        )

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"데이터 처리 및 DB 저장 중 오류 발생: {str(e)}")