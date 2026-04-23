import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI

# 1. 경로 설정 및 환경변수 로드 (가장 먼저 수행)
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# .env 파일 로드 (feat_backend 폴더 기준)
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

# 2. CV 모듈 및 라우터 Import
try:
    from feat_cv.cv import get_model_index_from_cache
except ImportError as e:
    print(f"❌ CV 모듈을 찾을 수 없습니다: {e}")
    get_model_index_from_cache = None

from app.api.v1.symptoms import symptom_router
from app.api.v1.body import body_router
from app.api.v1.taping import taping_router

# 3. FastAPI 앱 초기화 (단 한 번만 선언!)
app = FastAPI(title="AI Taping Guide API", version="1.0.0")

# 4. 서버 시작 시 실행될 이벤트 (Warm-up)
@app.on_event("startup")
async def startup_event():
    print("🚀 서버 시작: 3D 모델 통합 인덱스를 로드합니다...")
    print(f"[LOG] .env 로드 확인: API_KEY 존재 여부 -> {'성공' if os.getenv('AZURE_OPENAI_API_KEY') else '실패'}")
    
    if get_model_index_from_cache:
        try:
            get_model_index_from_cache()
            print("✅ 인덱스 로드 완료. 이제 모든 매칭이 0.1초 내에 처리됩니다.")
        except Exception as e:
            print(f"⚠️ 인덱스 로드 중 오류 발생: {e}")
    else:
        print("⚠️ CV 모듈 로드 실패로 인덱스를 미리 로드하지 못했습니다.")

# 5. 라우터 등록
app.include_router(symptom_router, prefix="/api/v1/symptoms", tags=["Symptoms"])
app.include_router(body_router, prefix="/api/v1/body", tags=["Body Match"])
app.include_router(taping_router, prefix="/api/v1/taping", tags=["Taping"])

@app.get("/")
def read_root():
    return {"message": "AI Taping Guide Backend is running!"}