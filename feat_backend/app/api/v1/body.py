import os
import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.concurrency import run_in_threadpool
from typing import Optional

from app.services.db_manager import db
import sys

# =====================================================================
# [CV 모듈 통합]
# =====================================================================
ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent
CV_PATH = ROOT_PATH / "feat_cv"

if str(CV_PATH) not in sys.path:
    sys.path.append(str(CV_PATH))

try:
    from cv import run_body_search_safe
    from resource_manager import download_azure_resources
    # 주의: 로컬 테스트 완료 후 배포 시에는 아래 함수 호출을 제어하거나 환경변수로 관리하세요.
    #download_azure_resources()
    
    print("[SUCCESS] CV 모듈(cv.py) 로드 완료")
except ImportError as e:
    print(f"[FATAL ERROR] CV 모듈 로드 실패: {e}")
    run_body_search_safe = None
# =====================================================================

body_router = APIRouter()

# 💡 [수정] C드라이브 하드코딩 제거 -> 프로젝트 루트 기준 상대 경로로 변경
UPLOAD_DIR = ROOT_PATH / "temp_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@body_router.post("/match")
async def match_body(
    session_id: str = Form(...),
    privacy_opt_out: bool = Form(False),
    image: Optional[UploadFile] = File(None)
):
    if not run_body_search_safe:
        raise HTTPException(status_code=500, detail="CV 시스템이 준비되지 않았습니다.")

    try:
        # 1. DB에서 EP1(증상 분석) 때 저장해둔 유저 신체 정보 가져오기
        session_data = db.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        user_input = session_data.get("user_input", {})
        physical_info = user_input.get("physical_info", {})
        
        height_cm = physical_info.get("height_cm")
        weight_kg = physical_info.get("weight_kg")
        sex = physical_info.get("gender")

        # 2. 이미지 임시 저장 (privacy_opt_out이 False일 때만)
        temp_image_path = None
        if not privacy_opt_out:
            if not image:
                raise HTTPException(status_code=400, detail="사진 제공 동의 시 이미지가 필수입니다.")
            
            ext = Path(image.filename).suffix
            temp_image_path = str(UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}")
            
            with open(temp_image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

        # 3. 무거운 CV 작업을 쓰레드풀에서 안전하게 실행
        cv_result = await run_in_threadpool(
            run_body_search_safe,
            image_path=temp_image_path,
            height_cm=height_cm,
            weight_kg=weight_kg,
            sex=sex,
            privacy_opt_out=privacy_opt_out
        )

        # 4. 에러 처리
        if cv_result.get("status") == "error":
            raise HTTPException(status_code=400, detail=cv_result.get("error", {}).get("message", "CV 분석 실패"))

        # 5. 성공 시 DB에 결과 업데이트
        best_model_id = cv_result.get("best_match", {}).get("model_id", "3148M")
        
        db.update_session(session_id, {
            "status": "BODY_MATCHED",
            "model_id": best_model_id,
            "cv_analysis_result": cv_result.get("user_features")
        })

        # 임시 이미지 파일 삭제
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)

        return {
            "session_id": session_id,
            "status": "BODY_MATCHED",
            "matched_model_id": best_model_id,
            "message": "체형 분석이 완료되었습니다."
        }

    except Exception as e:
        print(f"[ERROR] 체형 분석 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))