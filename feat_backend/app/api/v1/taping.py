import sys
import os
import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from pathlib import Path

logger = logging.getLogger(__name__)

# RAG 시스템 경로 설정
ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent
SCRIPTS_PATH = str(ROOT_PATH / "feat_llm" / "scripts")
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
    
    try:
        session_data = db.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

        full_model_id = session_data.get("model_id")
        raw_gender = session_data.get("sex")
        safe_gender = raw_gender.lower() if raw_gender else "none"
        body_part = session_data.get("body_part", "knee")

        # 🌟 1. 바디 모델 고정 로직 (3148/7136/Jerry)
        # 테이프 모델을 빌려오더라도 내 몸은 바뀌지 않도록 여기서 URL을 확정합니다.
        if not full_model_id or "JerryPing" in full_model_id:
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

        rag_input = {
            "structured_symptom": session_data.get("structured_symptom", {}),
            "search_filter": {"body_part": body_part}
        }

        llm_recommendation = rag_system.recommend(rag_input)
        options_data = llm_recommendation.get("options", [])
        safe_options = []

        for idx, opt in enumerate(options_data):
            tech_code = opt.get("technique_code", "KT_KNEE_GENERAL")
            asset_info = registry_manager.get_asset_urls(base_body_id, tech_code)
            
            # 레지스트리에 없으면 제리핑 모델이라도 빌려옴
            model_url = asset_info.get("combined_glb_url") or f"{BASE_STORAGE_URL}/{body_part}/JerryPing_{tech_code}.glb"
            video_url = asset_info.get("guide_video_url") or f"https://tapingdata1.blob.core.windows.net/videos/guides/{tech_code}.mp4"
                
            safe_options.append({
                "option_rank": idx + 1,
                "technique_code": tech_code,
                "model_url": model_url,
                "body_url": current_body_url, # 🌟 각 옵션에 내 몸 주소 주입 (복구용)
                "video_url": video_url,
                "title": opt.get("technique_name", "추천 테이핑"),
                "why": opt.get("why", "증상 분석에 따른 맞춤 테이핑입니다."), # 🌟 설명글 보장
                "coach": opt.get("coach", "안내에 따라 정확하게 부착해주세요."),
                "steps": opt.get("steps", []),
                "tape_type": opt.get("tape_type", "Kinesiology Tape"),
                "stretch_pct": opt.get("stretch_pct", 15)
            })

        # DB 업데이트
        db.update_session(session_id, {"taping_options": safe_options})
        
        return {
            "status": "success",
            "taping_options": safe_options
        }

    except Exception as e:
        logger.error(f"Recommend Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 🌟 2. [추가] 챗봇(테리) 응답 엔드포인트
@taping_router.post("/chat")
async def chat_with_terry(request: Request):
    if not rag_system:
        raise HTTPException(status_code=500, detail="LLM 시스템 준비 안됨")

    try:
        req_data = await request.json()
        session_id = req_data.get("session_id")
        user_message = req_data.get("message")
        current_step = req_data.get("current_step")
        instruction = req_data.get("instruction")

        # 세션 데이터 로드 (필요시 문맥 파악용)
        session_data = db.get_session(session_id)
        
        # RAG 시스템에 채팅 요청 (rag_system에 chat 기능이 있다고 가정)
        # 만약 별도 로직이 없다면 기본 응답을 생성합니다.
        if hasattr(rag_system, 'chat'):
            reply = rag_system.chat(user_message, current_step, instruction)
        else:
            reply = f"{current_step}단계 가이드에 대해 궁금하신 점을 확인했습니다. '{instruction}' 단계에서는 테이프를 너무 세게 당기지 않는 것이 중요해요. 더 궁금한 점이 있으신가요?"

        return {"reply": reply}

    except Exception as e:
        logger.error(f"Chat API Error: {e}")
        return {"reply": "죄송해요, 잠시 답변을 드릴 수 없어요. 가이드를 계속 진행하시겠어요?"}