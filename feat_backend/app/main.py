import os
import sys
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. 경로 설정 및 시스템 경로 추가 (app 모듈 인식용)
# 현재 파일 위치: .../feat_backend/app/main.py
# BACKEND_DIR: .../feat_backend (app 폴더의 부모)
BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# ROOT_DIR: .../main (feat_cv, feat_llm 등이 포함된 프로젝트 루트)
ROOT_DIR = BACKEND_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# 2. 환경변수 로드
# .env 파일이 feat_backend 폴더 안에 있으므로 BACKEND_DIR 기준 로드
ENV_PATH = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

# 환경변수 딕셔너리 강제 주입 (Azure 환경 대응)
config = dotenv_values(ENV_PATH)
for key, value in config.items():
    os.environ[key] = value

print(f"DEBUG: 환경변수 로드 완료. API KEY 존재 여부: {'AZURE_OPENAI_API_KEY' in os.environ}")

# 3. CV 모듈 임포트 (경로 추가 후 임포트 진행)
try:
    from feat_cv.cv import ensure_model_file_exists, get_model_index_from_cache
except ImportError as e:
    print(f"❌ CV 모듈 임포트 실패: {e}")
    ensure_model_file_exists = None
    get_model_index_from_cache = None

# 4. 라우터 임포트 (시스템 경로 추가 이후에 수행)
from app.api.v1.session import router as session_router
from app.api.v1.symptoms import symptom_router
from app.api.v1.body import body_router
from app.api.v1.taping import taping_router

# 5. FastAPI 앱 초기화
app = FastAPI(title="AI Taping Guide API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 보안 필요 시 프론트엔드 주소로 제한 가능
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
            import traceback
            traceback.print_exc()

# 7. 라우터 등록
app.include_router(session_router, prefix="/api/v1/session", tags=["Session"])
app.include_router(symptom_router, prefix="/api/v1/symptoms", tags=["Symptoms"])
app.include_router(body_router, prefix="/api/v1/body", tags=["Body"])
app.include_router(taping_router, prefix="/api/v1/taping", tags=["Taping"])

# 헬스체크 엔드포인트
@app.get("/")
async def root():
    return {"message": "AI Taping Guide API is running", "backend_dir": str(BACKEND_DIR)}