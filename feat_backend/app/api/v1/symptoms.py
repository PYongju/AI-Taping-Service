import sys
import os
from fastapi import APIRouter, HTTPException
import uuid
from datetime import datetime, timezone
from pathlib import Path

def get_project_root(target_name="main") -> Path:
    """현재 파일에서 위로 올라가며 폴더명이 'main'인 곳을 찾습니다."""
    current_path = Path(__file__).resolve()
    
    # 루트 폴더(/)까지 올라가며 확인
    for parent in [current_path] + list(current_path.parents):
        if parent.name == target_name:
            return parent
            
    # 만약 'main'이라는 이름을 못 찾으면 feat_backend의 상위를 기본값으로 사용
    return current_path.parent.parent 

# 1. 프로젝트의 진짜 최상위(main) 경로 확보
PROJECT_ROOT = get_project_root("main")

# 2. 메인 루트를 sys.path에 추가 (feat_cv, feat_llm 등 접근용)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 3. scripts 폴더 경로 설정 및 sys.path 추가 (ROOT_PATH 에러 수정 완료)
SCRIPTS_PATH = PROJECT_ROOT / "feat_llm" / "scripts"
if str(SCRIPTS_PATH) not in sys.path:
    sys.path.append(str(SCRIPTS_PATH))


# --- 이후부터는 기존과 동일하게 완벽합니다 ---
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