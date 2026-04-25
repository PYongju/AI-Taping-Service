import os
import shutil
import uuid
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.services.db_manager import db
from app.services.cv_module import body_analyzer 

logger = logging.getLogger(__name__)

body_router = APIRouter()
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

BASE_STORAGE_URL = "https://tapingdata1.blob.core.windows.net/models"

@body_router.post("/match")
async def match_body(
    session_id: str = Form(...),
    image: Optional[UploadFile] = File(None),
    height_cm: float = Form(175.0),
    weight_kg: float = Form(70.0),
    sex: Optional[str] = Form("none"), 
    privacy_opt_out: bool = Form(False)
):
    # 1. 이미지 저장
    saved_image_path = None
    if image and image.filename:
        try:
            file_ext = image.filename.split(".")[-1]
            saved_image_path = str(UPLOAD_DIR / f"{uuid.uuid4()}.{file_ext}")
            with open(saved_image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        except Exception as e:
            logger.error(f"[UPLOAD ERROR] {e}")

    # 2. 성별 값 정제 (소문자 통일)
    safe_sex = sex.lower() if sex else "none"

    # 3. CV 분석 실행
    cv_result = await body_analyzer.analyze_image(
        image_path=saved_image_path,
        height=height_cm,
        weight=weight_kg,
        gender=safe_sex,
        privacy_opt_out=privacy_opt_out
    )

    # 4. 🌟 모델 ID 결정 로직 (none 우선순위 강화)
    raw_model_id = cv_result.get("matched_model_id", "JerryPing")
    
    # 성별이 'none'이면 AI 결과와 상관없이 무조건 JerryPing 고정
    if safe_sex == "none":
        best_model_id = "JerryPing"
    
    # 성별이 male/female인 경우, AI가 JerryPing을 반환했다면 성별 기본값 적용
    elif "JerryPing" in raw_model_id:
        if safe_sex == "male":
            best_model_id = "3148M"
        elif safe_sex == "female":
            best_model_id = "7136F"
        else:
            best_model_id = "JerryPing"
    
    # AI가 구체적인 모델(예: 3148M_B)을 찾았다면 해당 모델 사용
    else:
        best_model_id = raw_model_id.split('_')[0] if "_" in raw_model_id else raw_model_id
    
    logger.info(f"🔥 [MATCH RESULT] 최종 결정된 모델 ID: {best_model_id} (성별: {safe_sex})")

    # 5. 폴더 및 파일 경로 분기
    if best_model_id == "JerryPing":
        folder = "body_privacy"
        suffix = "BODY"
    else:
        folder = "body"
        suffix = "BD_B"
    
    current_body_url = f"{BASE_STORAGE_URL}/{folder}/{best_model_id}_{suffix}.glb"

    # 6. DB 업데이트
    try:
        await run_in_threadpool(db.update_session, session_id, {
            "model_id": best_model_id,
            "glb_url": current_body_url,
            "sex": safe_sex,
            "status": "SCENE_4_COMPLETED"
        })
    except Exception as e:
        logger.error(f"[DB ERROR] {e}")

    return {
        "status": "success", 
        "model_id": best_model_id, 
        "glb_url": current_body_url
    }