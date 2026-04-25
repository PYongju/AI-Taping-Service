import sys
import os
import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# RAG 시스템 경로 설정
ROOT_PATH = r"C:\Users\USER\Desktop\AI_school2\main"
SCRIPTS_PATH = os.path.join(ROOT_PATH, "feat_llm", "scripts")
if SCRIPTS_PATH not in sys.path:
    sys.path.append(SCRIPTS_PATH)

from app.services.db_manager import db 
from app.services.registry_manager import registry_manager

try:
    from llm2 import TapingRAGSystem
    rag_system = TapingRAGSystem()
except ImportError as e:
    logger.error(f"[FATAL] llm2 import 실패: {e}")
    rag_system = None

taping_router = APIRouter()
BASE_STORAGE_URL = "https://tapingdata1.blob.core.windows.net/models"

@taping_router.post("/recommend")
async def recommend_taping(request: Request):
    if not rag_system:
        raise HTTPException(status_code=500, detail="LLM 시스템 준비 안됨")

    req_data = await request.json()
    session_id = req_data.get("session_id")
    model_id_from_req = req_data.get("model_id")

    try:
        session_data = db.get_session(session_id) or {}
        
        # 1. 정보 확정 (성별 none 체크)
        raw_gender = session_data.get("sex")
        safe_gender = raw_gender.lower() if raw_gender else "none"
        
        # 🌟 성별이 none이면 AI 결과가 DB에 저장되어 있더라도 JerryPing으로 덮어씀
        if safe_gender == "none":
            full_model_id = "JerryPing"
        else:
            full_model_id = model_id_from_req or session_data.get("model_id") or "JerryPing"
        
        print(f"DEBUG 1: 추천 단계 최종 ID = {full_model_id}, 성별 = {safe_gender}")

        # 2. 🌟 바디 모델 URL 결정 (사용자 요청 삼분할 적용)
        if safe_gender == "none":
            base_body_id = "JerryPing"
            current_body_url = f"{BASE_STORAGE_URL}/body_privacy/JerryPing_BODY.glb"
        elif "JerryPing" in full_model_id:
            if safe_gender == "male":
                base_body_id = "3148M"
                current_body_url = f"{BASE_STORAGE_URL}/body/3148M_BD_B.glb"
            elif safe_gender == "female":
                base_body_id = "7136F"
                current_body_url = f"{BASE_STORAGE_URL}/body/7136F_BD_B.glb"
            else:
                base_body_id = "JerryPing"
                current_body_url = f"{BASE_STORAGE_URL}/body_privacy/JerryPing_BODY.glb"
        else:
            base_body_id = full_model_id.split('_')[0]
            current_body_url = f"{BASE_STORAGE_URL}/body/{base_body_id}_BD_B.glb"
        
        # 3. RAG 추천 및 옵션 구성 (기존 로직 유지)
        user_input = session_data.get("user_input", {})
        body_part = user_input.get("body_part", "knee").lower()
        
        rag_input = {
            "session_id": session_id,
            "model_id": base_body_id,
            "body_part": body_part,
            "structured_symptom": session_data.get("structured_symptom", {}),
            "search_filter": {"body_part": body_part}
        }

        llm_recommendation = rag_system.recommend(rag_input)
        options_data = llm_recommendation.get("options", [])
        safe_options = []

        for idx, opt in enumerate(options_data):
            tech_code = opt.get("technique_code", "KT_KNEE_GENERAL")
            asset_info = registry_manager.get_asset_urls(base_body_id, tech_code)
            
            model_url = asset_info.get("combined_glb_url") or f"{BASE_STORAGE_URL}/{body_part}/JerryPing_{tech_code}.glb"
            video_url = asset_info.get("guide_video_url") or f"https://tapingdata1.blob.core.windows.net/videos/guides/{tech_code}.mp4"
                
            safe_options.append({
                "option_rank": idx + 1,
                "technique_code": tech_code,
                "model_url": model_url,
                "body_url": current_body_url, # 🌟 여기서 바디 주소 고정!
                "video_url": video_url,
                "title": opt.get("technique_name", "추천 테이핑"),
                "why": opt.get("why", ""),
                "steps": opt.get("steps", [])
            })

        return {
            "session_id": session_id,
            "glb_url": current_body_url,
            "options": safe_options
        }

    except Exception as e:
        logger.error(f"[ERROR] {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))