import sys
import os
from fastapi import APIRouter, HTTPException

# [경로 수정] scripts 폴더까지 path에 추가
ROOT_PATH = r"C:\Users\USER\Desktop\AI school 2차\main"
SCRIPTS_PATH = os.path.join(ROOT_PATH, "feat_llm", "scripts")

if SCRIPTS_PATH not in sys.path:
    sys.path.append(SCRIPTS_PATH)

from app.schemas.taping import TapingRequest, TapingResponse, TapingOption
from app.services.db_manager import db 
from app.services.registry_manager import registry_manager

try:
    from llm2 import TapingRAGSystem
    print("[SUCCESS] llm2 모듈 로드 완료!")
except ImportError as e:
    print(f"[FATAL ERROR] llm2 import 실패: {e}")
    TapingRAGSystem = None

rag_system = TapingRAGSystem() if TapingRAGSystem else None
taping_router = APIRouter()

@taping_router.post("/recommend", response_model=TapingResponse)
async def recommend_taping(request: TapingRequest):
    if not rag_system:
        raise HTTPException(status_code=500, detail="LLM 시스템이 초기화되지 않았습니다.")
    try:
        session_data = db.get_session(request.session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        user_input = session_data.get("user_input", {})
        rag_input = {
            "session_id": request.session_id,
            "model_id": session_data.get("model_id", "3148M"),
            "body_part": user_input.get("body_part", "knee"),
            "situation": user_input.get("situation", ""),
            "laterality": user_input.get("laterality", "right"),
            "raw_text": user_input.get("raw_text", ""),
            "structured_symptom": session_data.get("structured_symptom", {})
        }

        llm_recommendation = rag_system.recommend(rag_input)
        
        if llm_recommendation.get("redirect") == "hospital" or not llm_recommendation.get("options"):
            return TapingResponse(
                session_id=request.session_id,
                status="REDIRECT_HOSPITAL",
                analysis="급성 통증 또는 심한 부상이 의심됩니다.",
                options=[]
            )
        
        safe_options = []
        for idx, opt in enumerate(llm_recommendation.get("options", [])):
            tech_code = opt.get("technique_code", "UNKNOWN")
            asset_info = registry_manager.get_asset_urls(rag_input["model_id"], tech_code)
            
            safe_opt = TapingOption(
                option_rank=opt.get("option_rank", idx + 1),
                technique_code=tech_code,
                tape_type=opt.get("tape_type", "I-strip"),
                body_region=opt.get("body_region", "unknown"),
                why=opt.get("why", "근거를 찾을 수 없습니다."),
                anchor_position=opt.get("anchor_position", "부위 하단"),
                instruction=opt.get("instruction", "테이프를 부착하세요."),
                steps=opt.get("steps", []),
                combined_glb_url=asset_info["combined_glb_url"],
                guide_video_url=asset_info["guide_video_url"]
            )
            safe_options.append(safe_opt)

        final_analysis = llm_recommendation.get("analysis", "테이핑 옵션이 생성되었습니다.")
        db.update_session(request.session_id, {
            "status": "SCENE_6_COMPLETED",
            "taping_recommendations": [o.model_dump() for o in safe_options],
            "final_analysis": final_analysis
        })
        return TapingResponse(
            session_id=request.session_id,
            status="SCENE_6_COMPLETED",
            analysis=final_analysis,
            options=safe_options
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))