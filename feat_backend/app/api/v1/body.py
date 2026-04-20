from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import Optional
from app.schemas.body import BodyMatchResponse
from app.services.cv_module import body_analyzer
from app.services.db_manager import db
# from app.services.storage_manager import upload_file_to_blob  # 스토리지 직접 업로드 안 함 (비용/보안 최적화)

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
        print(f"[LOG] 체형 분석 요청 수신. Session: {session_id}")

        # ---------------------------------------------------------
        # 1. Null 값 체크 및 기본 모델 처리 (Fallback)
        # 키, 몸무게, 성별 중 하나라도 누락되면 지정된 기본 3D 모델 호출
        # ---------------------------------------------------------
        if height_cm is None or weight_kg is None or gender is None:
            print("[LOG] 필수 신체 정보 누락. 기본 3D 모델을 호출합니다.")
            default_model_id = "3148M" if gender == "male" else "7036F"
            
            fallback_update_data = {
                "status": "SCENE_3_COMPLETED",
                "body_match": {
                    "model_id": default_model_id,
                    "match_score": 1.0,
                    "base_glb_url": f"https://[YOUR_STORAGE].blob.core.windows.net/models/{default_model_id}_base.glb"
                }
            }
            # 세션 데이터 병합 (덮어쓰기 방지)
            db.update_session(session_id=session_id, update_data=fallback_update_data)
            
            return BodyMatchResponse(
                session_id=session_id,
                status="SCENE_3_COMPLETED",
                model_id=default_model_id,
                glb_url=fallback_update_data["body_match"]["base_glb_url"],
                match_type="default_fallback",
                metrics={}
            )

        # ---------------------------------------------------------
        # 2. In-Memory CV 분석 (정상 입력 시)
        # 파일을 저장하지 않고 바이트 데이터로 즉시 분석
        # ---------------------------------------------------------
        image_bytes = await image.read()
        print("[LOG] 이미지 메모리 적재 완료 (저장 생략)")

        analysis_result = await body_analyzer.analyze_image(
            image_bytes=image_bytes, # blob_url 대신 직접 전달
            height=height_cm, 
            weight=weight_kg,
            gender=gender
        )

        # ---------------------------------------------------------
        # 3. 스키마에 맞춘 DB 세션 업데이트 (update_session 사용)
        # ---------------------------------------------------------
        matched_model_id = analysis_result.get("matched_model_id", "3148M")
        
        session_update_data = {
            "status": "SCENE_3_COMPLETED",
            "body_match": {  # 문서화된 스키마 준수
                "model_id": matched_model_id,
                "match_score": analysis_result.get("shape_score", 0.95),
                "base_glb_url": f"https://[YOUR_STORAGE].blob.core.windows.net/models/{matched_model_id}_base.glb"
            }
        }
        
        # upsert_item 대신 병합 방식 사용
        db.update_session(session_id=session_id, update_data=session_update_data)
        print("[LOG] DB 세션 병합 업데이트 성공")

        # 4. 프론트엔드 응답
        return BodyMatchResponse(
            session_id=session_id,
            status="SCENE_3_COMPLETED",
            model_id=matched_model_id,
            glb_url=session_update_data["body_match"]["base_glb_url"],
            match_type="cv_analyzed",
            metrics=analysis_result.get("metrics", {})
        )

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"체형 분석 파이프라인 에러: {str(e)}")