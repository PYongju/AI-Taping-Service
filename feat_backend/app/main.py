import os
import sys
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 1. 경로 설정
BACKEND_DIR = Path(__file__).resolve().parent.parent

# 파이썬이 'app.api...'를 찾을 수 있도록 feat_backend 폴더를 시스템 경로에 최우선으로 추가
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# 시스템 경로가 추가된 이후에 라우터를 임포트해야 에러가 나지 않습니다.
from app.api.v1.session import router as session_router

# .env 경로 지정 (수정됨)
ENV_PATH = BACKEND_DIR / ".env"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# 2. 환경변수 로드 및 강제 주입
load_dotenv(dotenv_path=ENV_PATH, override=True)
config = dotenv_values(ENV_PATH)
for key, value in config.items():
    os.environ[key] = value

print(f"DEBUG: 환경변수 로드 완료. API KEY 존재 여부: {'AZURE_OPENAI_API_KEY' in os.environ}")

# 3. CV 모듈 임포트
try:
    # CV 폴더는 최상위 루트에 있으므로, 최상위 경로도 추가해줍니다.
    ROOT_DIR = BACKEND_DIR.parent
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))
        
    from feat_cv.cv import ensure_model_file_exists, get_model_index_from_cache
except ImportError as e:
    print(f"❌ CV 모듈 임포트 실패: {e}")
    ensure_model_file_exists = None
    get_model_index_from_cache = None

# 4. 나머지 라우터 임포트
from app.api.v1.symptoms import symptom_router
from app.api.v1.body import body_router
from app.api.v1.taping import taping_router

# 5. FastAPI 초기화 (이하 기존 코드와 동일)
app = FastAPI(title="AI Taping Guide API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 프론트엔드 주소 명시
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
            print("✅ 서버 준비 완료! 이제 모든 매칭이 0.1초 내에 처리됩니다.")
        except Exception as e:
            print(f"⚠️ 초기화 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️ CV 모듈 로드 실패로 인덱스를 로드하지 못했습니다.")

# 7. 라우터 등록
app.include_router(symptom_router, prefix="/api/v1/symptoms", tags=["Symptoms"])
app.include_router(body_router, prefix="/api/v1/body", tags=["Body Match"])
app.include_router(taping_router, prefix="/api/v1/taping", tags=["Taping"])
app.include_router(session_router, prefix="/api/v1/session", tags=["session"])

@app.get("/")
def read_root():
    return {"message": "AI Taping Guide Backend is running!"}