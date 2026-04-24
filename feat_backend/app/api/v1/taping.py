import sys
import os
import logging
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

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
        
        # 🌟 수정: model_id에서 순수 바디 ID(예: JerryPing)만 추출하여 중복 방지
        full_model_id = session_data.get("model_id", "JerryPing_KT_KNEE_GENERAL")
        base_body_id = full_model_id.split('_')[0] 
        
        user_input = session_data.get("user_input", {})
        body_part = user_input.get("body_part", "knee").lower()
        
        # RAG 검색 시 body_part를 명시적으로 강조하여 엉뚱한 부위(Neck 등)가 안 나오게 함
        rag_input = {
            "session_id": session_id,
            "model_id": full_model_id,
            "body_part": body_part,
            "situation": user_input.get("situation", ""),
            "laterality": user_input.get("laterality", "right"),
            "raw_text": user_input.get("raw_text", ""),
            "structured_symptom": session_data.get("structured_symptom", {}),
            "search_filter": {"body_part": body_part} # 검색 필터 강화
        }

        llm_recommendation = rag_system.recommend(rag_input)
        
        if llm_recommendation.get("redirect") == "hospital":
            return {"session_id": session_id, "status": "REDIRECT_HOSPITAL", "options": []}

        options_data = llm_recommendation.get("options", [])
        safe_options = []
        
        for idx, opt in enumerate(options_data):
            tech_code = opt.get("technique_code", "KT_KNEE_GENERAL")
            
            # 🌟 핵심 수정: base_body_id(JerryPing)와 tech_code(KT_KNEE_GENERAL)를 사용하여 매칭
            # registry_manager 내부에서 JerryPing + _ + KT_KNEE_GENERAL 조합으로 키 생성
            try:
                asset_info = registry_manager.get_asset_urls(base_body_id, tech_code)
                model_url = asset_info.get("mesh_file") or asset_info.get("combined_glb_url")
                video_url = asset_info.get("guide_video_url")
            except Exception as e:
                logger.warning(f"매칭 실패: {e}")
                model_url = None
                video_url = None
            
            # Fallback (구조 유지)
            if not model_url:
                model_url = f"https://tapingdata1.blob.core.windows.net/models/knee/{base_body_id}_{tech_code}.glb"
            if not video_url:
                video_url = f"https://tapingdata1.blob.core.windows.net/videos/guides/{tech_code}.mp4"
            
            safe_options.append({
                "option_rank": idx + 1,
                "registry_key": f"{base_body_id}_{tech_code}", # 🌟 중복 방지된 정상 키
                "taping_id": tech_code,
                "title": opt.get("technique_name", "추천 테이핑"),
                "name": opt.get("technique_name", "추천 테이핑"),
                "tape_type": opt.get("tape_type", "Guide"),
                "stretch_pct": opt.get("stretch_pct", 0),
                "why": opt.get("why", "분석된 추천 사유입니다."),
                "coach": opt.get("instruction", "안내에 따라 진행해주세요."), 
                "steps": opt.get("steps", []),
                "step_glb_urls": opt.get("step_glb_urls", []), 
                "model_url": model_url,
                "video_url": video_url,
                "disclaimer": llm_recommendation.get("disclaimer", "예방을 위한 가이드입니다.")
            })

        # 최종 반환 데이터 구성
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