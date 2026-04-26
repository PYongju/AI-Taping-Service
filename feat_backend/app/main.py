import os
import sys
from pathlib import Path  # 가장 먼저 선언

# 1. 경로 설정
CURRENT_FILE_PATH = Path(__file__).resolve()
BACKEND_DIR = CURRENT_FILE_PATH.parent.parent
ROOT_DIR = BACKEND_DIR.parent

# 파이썬 경로 주입
for p in [str(BACKEND_DIR), str(ROOT_DIR), str(ROOT_DIR / "feat_llm" / "scripts"), str(ROOT_DIR / "feat_cv")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# 2. 필수 라이브러리 로드
from dotenv import load_dotenv, dotenv_values
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 3. 환경변수 주입
ENV_PATH = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)
config = dotenv_values(ENV_PATH)
for key, value in config.items():
    os.environ[key] = value

# 4. 모듈 임포트
try:
    from feat_cv.cv import ensure_model_file_exists, get_model_index_from_cache
except Exception:
    ensure_model_file_exists = None
    get_model_index_from_cache = None

from app.api.v1.session import router as session_router
from app.api.v1.symptoms import symptom_router
from app.api.v1.body import body_router
from app.api.v1.taping import taping_router

# 5. 앱 실행
app = FastAPI(title="AI Taping Guide API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_event():
    if ensure_model_file_exists:
        ensure_model_file_exists()
        get_model_index_from_cache()

app.include_router(symptom_router, prefix="/api/v1/symptoms", tags=["Symptoms"])
app.include_router(body_router, prefix="/api/v1/body", tags=["Body"])
app.include_router(taping_router, prefix="/api/v1/taping", tags=["Taping"])
app.include_router(session_router, prefix="/api/v1/session", tags=["Session"])

@app.get("/")
async def root():
    return {"status": "ok"}