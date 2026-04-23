import sys
import os
from fastapi import APIRouter, HTTPException
import uuid
from datetime import datetime, timezone

# [경로 수정] scripts 폴더까지 path에 추가
ROOT_PATH = r"C:\Users\USER\Desktop\AI school 2차\main"
SCRIPTS_PATH = os.path.join(ROOT_PATH, "feat_llm", "scripts")

if SCRIPTS_PATH not in sys.path:
    sys.path.append(SCRIPTS_PATH)

from app.schemas.symptoms import SymptomRequest, SymptomResponse, StructuredSymptom
from app.services.db_manager import db 

try:
    from llm_structure_symptom import SymptomStructurer
    print("[SUCCESS] 증상 구조화 LLM 모듈 로드 완료!")
except ImportError as e:
    print(f"[FATAL ERROR] 증상 구조화 LLM 로드 실패: {e}")
    SymptomStructurer = None

structurer = SymptomStructurer() if SymptomStructurer else None
symptom_router = APIRouter()

@symptom_router.post("/analyze", response_model=SymptomResponse)
async def analyze_symptoms(request: SymptomRequest):
    try:
        new_session_id = f"sess_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
        now_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        llm_input = {
            "body_part": request.body_part,
            "situation": request.situation,
            "symptom_type": request.symptom_type or "custom", 
            "user_text": request.raw_text 
        }

        if structurer:
            llm_response = structurer.structure(llm_input)
            symptom_data = llm_response.get("structured_symptom", {})
            structured_symptom_data = StructuredSymptom(
                area=symptom_data.get("area", request.body_part),
                keywords=symptom_data.get("keywords", [request.situation, "통증"]),
                summary=symptom_data.get("summary", "증상 분석이 완료되었습니다.")
            )
        else:
            structured_symptom_data = StructuredSymptom(
                area=request.body_part,
                keywords=[request.situation, "통증"],
                summary=f"{request.body_part} 증상 분석 완료 (Mock)"
            )

        session_document = {
            "id": new_session_id, 
            "session_id": new_session_id, 
            "status": "SYMPTOMS_ANALYZED", 
            "created_at": now_time, 
            "updated_at": now_time, 
            "user_input": { 
                "body_part": request.body_part,
                "situation": request.situation,
                "raw_text": request.raw_text,
                "symptom_type": request.symptom_type, 
                "physical_info": { "height_cm": request.height_cm, "weight_kg": request.weight_kg, "gender": request.gender }
            },
            "structured_symptom": structured_symptom_data.model_dump()
        }
    
        db.create_session(session_document)
        return SymptomResponse(session_id=new_session_id, status="SYMPTOMS_ANALYZED", structured_symptom=structured_symptom_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))