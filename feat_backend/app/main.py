import os
import sys
from pathlib import Path  # 1. Path를 가장 먼저 임포트해야 에러가 나지 않습니다.

# ---------------------------------------------------------
# 1. 경로 설정 및 강제 주입 (이 부분이 모든 에러를 해결합니다)
# ---------------------------------------------------------
# 현재 main.py 위치 기준: .../feat_backend/app/main.py
CURRENT_FILE_PATH = Path(__file__).resolve()
BACKEND_DIR = CURRENT_FILE_PATH.parent.parent  # .../feat_backend
ROOT_DIR = BACKEND_DIR.parent                 # .../main (최상위)

# 파이썬이 모듈을 찾을 수 있도록 경로 목록에 추가
# 1. BACKEND_DIR: 'app.api...'를 찾기 위함
# 2. ROOT_DIR: 'feat_cv', 'feat_llm' 등을 찾기 위함
# 3. scripts 폴더: 'llm_structure_symptom' 등을 찾기 위함
extra_paths = [
    str(BACKEND_DIR),
    str(ROOT_DIR),
    str(ROOT_DIR / "feat_llm" / "scripts"),
    str(ROOT_DIR / "feat_cv")
]

for p in extra_paths:
    if p not in sys.path:
        sys.path.insert(0, p)

# ---------------------------------------------------------
# 2. 필수 라이브러리 임포트 및 환경변수 로드
# ---------------------------------------------------------
from dotenv import load_dotenv, dotenv_values
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# .env 로드
ENV_PATH = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

# Azure 운영 환경 대응을 위한 환경변수 강제 주입
config = dotenv_values(ENV_PATH)
for key, value in config.items():
    os.environ[key] = value

print(f"DEBUG: 환경변수 로드 완료. API KEY 존재 여부: {'AZURE_OPENAI_API_KEY' in os.environ}")

# ---------------------------------------------------------
# 3. 기능 모듈 및 라우터 임포트 (경로 설정 완료 후 진행)
# ---------------------------------------------------------
# CV 모듈 임포트 시도
try:
    from feat_cv.cv import ensure_model_file_exists, get_model_index_from_cache
    print("✅ CV 모듈 로드 성공")
except Exception as e:
    print(f"❌ CV 모듈 임포트 실패: {e}")
    ensure_model_file_exists = None
    get_model_index_from_cache = None

# 나머지 라우터 임포트
from app.api.v1.session import router as session_router
from app.api.v1.symptoms import symptom_router
from app.api.v1.body import body_router
from app.api.v1.taping import taping_router

# ---------------------------------------------------------
# 4. FastAPI 초기화 및 설정
# ---------------------------------------------------------
app = FastAPI(title="AI Taping Guide API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 보안 필요 시 특정 도메인으로 제한 가능
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. 서버 시작 시 실행되는 이벤트
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

# 6. 라우터 등록
app.include_router(symptom_router, prefix="/api/v1/symptoms", tags=["Symptoms"])
app.include_router(body_router, prefix="/api/v1/body", tags=["Body Match"])
app.include_router(taping_router, prefix="/api/v1/taping", tags=["Taping"])
app.include_router(session_router, prefix="/api/v1/session", tags=["Session"])

@app.get("/")
def read_root():
    return {"message": "AI Taping Guide Backend is running!", "status": "online"}