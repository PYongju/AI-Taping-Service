# app/api/v1/taping.py

import sys
import os
import logging
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

# 🌟 1. 방금 수정한 schemas에서 정확한 설계도를 가져옵니다!
from app.schemas.taping import TapingResponse

ROOT_PATH = r"C:\Users\USER\Desktop\AI_school2\main"
SCRIPTS_PATH = os.path.join(ROOT_PATH, "feat_llm", "scripts")
if SCRIPTS_PATH not in sys.path:
    sys.path.append(SCRIPTS_PATH)

from app.services.db_manager import db 
from app.services.registry_manager import registry_manager

try:
    from llm2 import TapingRAGSystem
    logger.info("[SUCCESS] llm2 모듈 로드 완료!")
except ImportError as e:
    logger.error(f"[FATAL ERROR] llm2 import 실패: {e}")
    TapingRAGSystem = None

rag_system = TapingRAGSystem() if TapingRAGSystem else None
taping_router = APIRouter()

# 🌟 2. response_model을 지정하여 데이터가 완벽하게 통과되도록 합니다.
@taping_router.post("/recommend")
async def recommend_taping(request: dict):
    if not rag_system:
        raise HTTPException(status_code=500, detail="LLM 시스템이 초기화되지 않았습니다.")
    
    session_id = request.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id가 필요합니다.")

    try:
        session_data = db.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        full_model_id = session_data.get("model_id", "JerryPing_KT_KNEE_GENERAL")
        base_body_id = full_model_id.split('_')[0] 
        
        user_input = session_data.get("user_input", {})
        body_part = user_input.get("body_part", "knee").lower()
        
        rag_input = {
            "session_id": session_id,
            "model_id": full_model_id,
            "body_part": body_part,
            "situation": user_input.get("situation", ""),
            "laterality": user_input.get("laterality", "right"),
            "raw_text": user_input.get("raw_text", ""),
            "structured_symptom": session_data.get("structured_symptom", {}),
            "search_filter": {"body_part": body_part}
        }

        llm_recommendation = rag_system.recommend(rag_input)

        print("\n=== [DEBUG] LLM 원본 응답 ===")
        print(llm_recommendation)
        print("==============================\n")
        
        if llm_recommendation.get("redirect") == "hospital":
            return {"session_id": session_id, "status": "REDIRECT_HOSPITAL", "analysis": "병원 권장", "options": []}

        options_data = llm_recommendation.get("options", [])
        safe_options = []
        
        for idx, opt in enumerate(options_data):
            tech_code = opt.get("technique_code", "KT_KNEE_GENERAL")
            
            # 🌟 3. LLM 데이터 가공
            llm_steps = opt.get("steps", [])
            formatted_steps = []
            for s in llm_steps:
                formatted_steps.append({
                    "step": s.get("step", idx + 1),
                    "title": s.get("title", f"단계 {s.get('step', 1)}"),
                    "instruction": s.get("instruction", "상세 가이드가 없습니다."),
                    "pose": s.get("pose", "화면의 안내 자세를 유지해 주세요."),
                    "warn": s.get("warn", "통증이 느껴지면 즉시 중단하세요.")
                })

            try:
                asset_info = registry_manager.get_asset_urls(base_body_id, tech_code)
                model_url = asset_info.get("mesh_file") or asset_info.get("combined_glb_url")
                video_url = asset_info.get("guide_video_url")
            except Exception as e:
                logger.warning(f"매칭 실패: {e}")
                model_url = None
                video_url = None
            
            if not model_url:
                model_url = f"https://tapingdata1.blob.core.windows.net/models/knee/{base_body_id}_{tech_code}.glb"
            if not video_url:
                video_url = f"https://tapingdata1.blob.core.windows.net/videos/guides/{tech_code}.mp4"
            
            safe_options.append({
                "option_rank": idx + 1,
                "registry_key": f"{base_body_id}_{tech_code}",
                "taping_id": tech_code,
                "technique_code": tech_code,
                "title": opt.get("technique_name", "추천 테이핑"),
                "name": opt.get("technique_name", "추천 테이핑"),
                "tape_type": opt.get("tape_type", "Guide"),
                "stretch_pct": opt.get("stretch_pct", 0),
                "why": opt.get("why", "분석된 추천 사유입니다."),
                "coach": opt.get("instruction", "안내에 따라 진행해주세요."), 
                "steps": formatted_steps, 
                "step_glb_urls": opt.get("step_glb_urls", []), 
                "model_url": model_url,
                "video_url": video_url,
                "disclaimer": llm_recommendation.get("disclaimer", "예방을 위한 가이드입니다.")
            })

        final_analysis = llm_recommendation.get("analysis", "테이핑 가이드가 생성되었습니다.")
        db.update_session(session_id, {
            "status": "SCENE_6_COMPLETED",
            "taping_recommendations": safe_options,
            "final_analysis": final_analysis
        })
        
        return {
            "session_id": session_id,
            "status": "SCENE_6_COMPLETED",
            "analysis": final_analysis,
            "options": safe_options
        }
        
    except Exception as e:
        logger.error(f"[ERROR] {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))