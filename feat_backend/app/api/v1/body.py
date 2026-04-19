from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import Optional
from app.schemas.body import BodyMatchResponse

body_router = APIRouter()

@body_router.post("/match", response_model=BodyMatchResponse)
async def match_body(
    session_id: str = Form(...),
    image: UploadFile = File(...),
    height_cm: Optional[float] = Form(None),
    weight_kg: Optional[float] = Form(None),
    gender: Optional[str] = Form(None)
):
    try:
        # UX 기획 문서 반영: 성별 미입력 시 남성 카데바(기본 모델) 폴백 처리
        actual_gender = gender if gender else "male"
        
        print(f"[LOG] 체형 분석 요청 수신. Session: {session_id}")
        print(f"[LOG] 파일명: {image.filename}, 적용 성별: {actual_gender}")

        # TODO: 이미지 임시 저장 -> CV 모듈(MediaPipe) 분석 -> DB 세션 업데이트 (PATCH)

        # 프론트엔드 테스트를 위한 가짜(Mock) 응답 데이터 반환
        return BodyMatchResponse(
            session_id=session_id,
            status="SCENE_3_COMPLETED",
            model_id="M0234",
            glb_url="https://[YOUR_STORAGE].blob.core.windows.net/models/M0234_base.glb",
            match_type="heuristic_reranked",
            metrics={"shape_score": 0.94}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))