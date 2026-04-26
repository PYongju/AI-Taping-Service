import os
import sys
from pathlib import Path  # ⭐️ Path 정의를 최상단으로 이동하여 NameError 해결

# 1. 모든 피처 폴더 경로 강제 등록 (경로 에러 해결사)
# 현재 파일 위치: .../feat_backend/app/main.py
CURRENT_FILE_PATH = Path(__file__).resolve()
BACKEND_DIR = CURRENT_FILE_PATH.parent.parent  # feat_backend
ROOT_DIR = BACKEND_DIR.parent                 # main

# 파이썬이 검색할 경로 목록에 피처 폴더들 추가 (ModuleNotFoundError 해결)
extra_paths = [
    str(BACKEND_DIR),                               
    str(ROOT_DIR),                                  
    str(ROOT_DIR / "feat_llm" / "scripts"),         
    str(ROOT_DIR / "feat_cv")                       
]

for p in extra_paths:
    if p not in sys.path:
        sys.path.insert(0, p)

# 2. 필수 라이브러리 및 환경변수 로드
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, dotenv_values

# .env 로드 및 환경변수 주입
ENV_PATH = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)
config = dotenv_values(ENV_PATH)
for key, value in config.items():
    os.environ[key] = value

print(f"DEBUG: 환경변수 로드 완료. API KEY 존재 여부: {'AZURE_OPENAI_API_KEY' in os.environ}")

# 3. CV 및 LLM 모듈 임포트 시도 (위에서 경로를 주입했으므로 이제 정상 작동함)
try:
    from feat_cv.cv import ensure_model_file_exists, get_model_index_from_cache
    print("✅ CV 모듈 로드 성공")
except Exception as e:
    print(f"❌ CV 모듈 임포트 실패: {e}")
    ensure_model_file_exists = None
    get_model_index_from_cache = None

# 4. 라우터 임포트
from app.api.v1.session import router as session_router
from app.api.v1.symptoms import symptom_router
from app.api.v1.body import body_router
from app.api.v1.taping import taping_router

# 5. FastAPI 앱 초기화
app = FastAPI(title="AI Taping Guide API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. 서버 시작 시 실행되는 이벤트
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