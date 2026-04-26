import os
import sys
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. 모든 피처 폴더 경로 강제 등록 (경로 에러 해결사)
BACKEND_DIR = Path(__file__).resolve().parent.parent # feat_backend
ROOT_DIR = BACKEND_DIR.parent                       # main

# 파이썬이 검색할 경로 목록에 피처 폴더들 추가
extra_paths = [
    str(BACKEND_DIR),                               # app 폴더 인식용
    str(ROOT_DIR),                                  # feat_cv, feat_llm 폴더 인식용
    str(ROOT_DIR / "feat_llm" / "scripts"),         # llm_structure_symptom 인식용
    str(ROOT_DIR / "feat_cv")                       # cv 모듈 인식용
]

for p in extra_paths:
    if p not in sys.path:
        sys.path.insert(0, p)

# 2. 라우터 및 환경변수 로드
from app.api.v1.session import router as session_router

ENV_PATH = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

config = dotenv_values(ENV_PATH)
for key, value in config.items():
    os.environ[key] = value

print(f"DEBUG: 환경변수 로드 완료. API KEY 존재 여부: {'AZURE_OPENAI_API_KEY' in os.environ}")

# 3. CV 및 LLM 모듈 임포트 시도
try:
    from feat_cv.cv import ensure_model_file_exists, get_model_index_from_cache
    print("✅ CV 모듈 로드 성공")
except Exception as e:
    print(f"❌ CV 모듈 임포트 실패: {e}")
    ensure_model_file_exists = None
    get_model_index_from_cache = None

# 4. 나머지 라우터 임포트
from app.api.v1.symptoms import symptom_router
from app.api.v1.body import body_router
from app.api.v1.taping import taping_router

# 5. FastAPI 초기화
app = FastAPI(title="AI Taping Guide API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. 서버 시작 시 실행
@app.on_event("startup")
async def startup_event():
    print("🚀 서버 시작: 3D 모델 통합 인덱스를 로드합니다...")
    if ensure_model_file_exists and get_model_index_from_cache:
        try:
            ensure_model_file_exists()
            get_model_index_from_cache()
            print("✅ 서버 준비 완료! 모델 인덱싱이 완료되었습니다.")
        except Exception as e:
            print(f"⚠️ 초기화 중 오류 발생: {e}")

# 7. 라우터 등록
app.include_router(session_router, prefix="/api/v1/session", tags=["Session"])
app.include_router(symptom_router, prefix="/api/v1/symptoms", tags=["Symptoms"])
app.include_router(body_router, prefix="/api/v1/body", tags=["Body"])
app.include_router(taping_router, prefix="/api/v1/taping", tags=["Taping"])

@app.get("/")
async def root():
    return {"message": "AI Taping Guide API is running", "status": "online"}