import sys
import os
import logging
from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger(__name__)

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

    try:
        req_data = await request.json()
        session_id = req_data.get("session_id")
        model_id_from_req = req_data.get("model_id")

        # None 방어
        session_data = db.get_session(session_id) or {}
        raw_gender = session_data.get("sex")
        safe_gender = str(raw_gender).lower() if raw_gender else "none"
        
        if safe_gender == "none":
            full_model_id = "JerryPing"
        else:
            full_model_id = model_id_from_req or session_data.get("model_id") or "JerryPing"
        
        # 바디 URL 세팅
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
        
        user_input = session_data.get("user_input") or {}
        raw_body_part = user_input.get("body_part") or "knee"
        body_part = str(raw_body_part).lower()
        
        rag_input = {
            "session_id": session_id,
            "model_id": base_body_id,
            "body_part": body_part,
            "structured_symptom": session_data.get("structured_symptom") or {},
            "search_filter": {"body_part": body_part}
        }

        llm_recommendation = {}
        try:
            llm_recommendation = rag_system.recommend(rag_input) or {}
        except Exception as e:
            logger.error(f"RAG Recommend Error: {e}")

        options_data = llm_recommendation.get("options") or []
        safe_options = []

        for idx, opt in enumerate(options_data):
            tech_code = opt.get("technique_code", "KT_KNEE_GENERAL")
            
            asset_info = {}
            try:
                asset_info = registry_manager.get_asset_urls(base_body_id, tech_code) or {}
            except Exception as e:
                pass
            
            model_url = asset_info.get("combined_glb_url") or f"{BASE_STORAGE_URL}/{body_part}/JerryPing_{tech_code}.glb"
            video_url = asset_info.get("guide_video_url") or f"https://tapingdata1.blob.core.windows.net/videos/guides/{tech_code}.mp4"
                
            safe_options.append({
                "option_rank": idx + 1,
                "technique_code": tech_code,
                "model_url": model_url,
                "body_url": current_body_url,
                "video_url": video_url,
                "title": opt.get("technique_name", "추천 테이핑"),
                "why": opt.get("why", "분석 결과에 따른 맞춤 테이핑 기법입니다."),
                "coach": opt.get("coach", "안내에 따라 정확한 위치에 부착해주세요."),
                "steps": opt.get("steps", []),
                "tape_type": opt.get("tape_type", "Kinesiology Tape"),
                "stretch_pct": opt.get("stretch_pct", 15)
            })

        try:
            db.update_session(session_id, {
                "taping_options": safe_options,
                "glb_url": current_body_url
            })
        except Exception as e:
            logger.error(f"DB Update Error: {e}")

        return {
            "status": "success",
            "session_id": session_id,
            "glb_url": current_body_url,
            "options": safe_options,
            "taping_options": safe_options
        }

    except Exception as e:
        logger.error(f"[ERROR] recommend_taping: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 에러 발생: {str(e)}")

# 🌟 챗봇 연동
@taping_router.post("/chat")
async def chat_with_terry(request: Request):
    try:
        req_data = await request.json()
        current_step = req_data.get("current_step", 1)
        instruction = req_data.get("instruction", "")
        user_message = req_data.get("message", "")

        if not rag_system:
            return {"reply": "LLM 두뇌가 아직 연결되지 않았습니다."}

        # 🌟 방금 llm2.py에 추가한 그 chat 함수를 직접 호출합니다!
        if hasattr(rag_system, 'chat'):
            # 우리가 llm2.py에 만든 함수는 (질문, 현재단계, 설명) 3가지를 받도록 되어있습니다.
            reply_text = rag_system.chat(user_message, current_step, instruction)
        else:
            # 만약 함수를 못 찾을 경우 (거의 발생하지 않음)
            reply_text = "테리의 챗봇 기능이 아직 연결되지 않았어요."
            
        return {"reply": reply_text}

    except Exception as e:
        logger.error(f"Chat API Error: {e}")
        return {"reply": "앗! 답변을 생각하다가 머리가 엉켰어요. 다시 물어봐주시겠어요?"}

    except Exception as e:
        logger.error(f"Chat API Error: {e}")
        return {"reply": "서버랑 통신하다가 문제가 생겼어요."}
# 🌟 결과 저장
@taping_router.post("/save")
async def save_taping_result(request: Request):
    try:
        req_data = await request.json()
        session_id = req_data.get("session_id")
        taping_id = req_data.get("taping_id")
        if session_id:
            db.update_session(session_id, {"saved_taping_id": taping_id, "status": "completed"})
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="저장 중 에러 발생")