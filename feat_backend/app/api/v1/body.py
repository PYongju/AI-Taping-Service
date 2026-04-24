import os
import shutil
import uuid
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.services.db_manager import db
# 🌟 registry_manager 임포트 (데이터 매칭용)
from app.services.registry_manager import registry_manager 
import sys

logger = logging.getLogger(__name__)

# [CV 모듈 통합]
ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent
CV_PATH = ROOT_PATH / "feat_cv"
if str(CV_PATH) not in sys.path:
    sys.path.append(str(CV_PATH))

try:
    from cv import run_body_search_safe
except ImportError:
    run_body_search_safe = None

body_router = APIRouter()
UPLOAD_DIR = ROOT_PATH / "temp_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@body_router.post("/match")
async def match_body(
    session_id: str = Form(...),
    privacy_opt_out: bool = Form(False),
    height_cm: Optional[float] = Form(None),
    weight_kg: Optional[float] = Form(None),
    sex: Optional[str] = Form(None),
    image_path: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None)
):
    session_data = db.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    # 🌟 1. 한글 입력 방어: 부위명(part)을 강제로 영문 규격으로 변환
    part_map = {"무릎": "knee", "발목": "ankle", "손목": "wrist"}
    raw_part = session_data.get("part", "knee")
    final_part = part_map.get(raw_part, raw_part)

    # 파라미터 정리
    physical_info = session_data.get("user_input", {}).get("physical_info", {})
    final_height = height_cm or physical_info.get("height_cm")
    final_weight = weight_kg or physical_info.get("weight_kg")
    final_sex = sex or physical_info.get("gender")

    # 이미지 처리... (생략)
    # ... (기존 이미지 저장 로직 유지) ...

    # 2. CV 분석 실행
    try:
        cv_result = await run_in_threadpool(
            run_body_search_safe,
            image_path=None, # 예시용
            height_cm=final_height,
            weight_kg=final_weight,
            sex=final_sex,
            privacy_opt_out=privacy_opt_out
        )
    except Exception:
        cv_result = {"status": "error"}

    # 3. 모델 ID 결정 (Fallback: JerryPing)
    best_model_id = cv_result.get("best_match", {}).get("model_id", "JerryPing")
    
    # 🌟 4. [핵심] taping_options 생성 및 URL 매칭
    # 여기서는 예시로 일반 옵션을 생성합니다. 실제 로직에 맞게 수정하세요.
    taping_options = [
        {
            "registry_key": "KT_KNEE_GENERAL",
            "title": "무릎 테이핑 (일반)",
            "model_url": "", # 아래에서 주입
            "video_url": ""
        }
    ]
    
    for opt in taping_options:
        assets = registry_manager.get_asset_urls(best_model_id, opt["registry_key"])
        opt["model_url"] = assets.get("combined_glb_url", "")
        opt["video_url"] = assets.get("guide_video_url", "")

    # DB 업데이트
    db.update_session(session_id, {
        "status": "BODY_MATCHED",
        "model_id": best_model_id,
        "taping_options": taping_options
    })

    # 🌟 5. [핵심] 프론트엔드가 기대하는 JSON 응답 반환
    return {
        "session_id": session_id,
        "status": "BODY_MATCHED",
        "matched_model_id": best_model_id,
        "taping_options": taping_options  # 이 키가 있어야 프론트엔드 에러가 사라집니다.
    }