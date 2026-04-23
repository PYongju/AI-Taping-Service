import os
from pathlib import Path
from dotenv import load_dotenv

# 1. feat_backend 폴더에 있는 .env 파일을 정확하게 조준합니다!
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# 강제로 환경변수에 밀어넣기
load_dotenv(dotenv_path=ENV_PATH, override=True)

print(f"[LOG] .env 파일 위치: {ENV_PATH}")
print(f"[LOG] .env 로드 확인: API_KEY 존재 여부 -> {'성공' if os.getenv('AZURE_OPENAI_API_KEY') else '실패'}")

# 2. 이후 라우터들을 import 합니다.
from fastapi import FastAPI
from app.api.v1.symptoms import symptom_router
from app.api.v1.body import body_router
from app.api.v1.taping import taping_router

app = FastAPI(title="AI Taping Guide API", version="1.0.0")

app.include_router(symptom_router, prefix="/api/v1/symptoms", tags=["Symptoms"])
app.include_router(body_router, prefix="/api/v1/body", tags=["Body Match"])
app.include_router(taping_router, prefix="/api/v1/taping", tags=["Taping"])

@app.get("/")
def read_root():
    return {"message": "AI Taping Guide Backend is running!"}