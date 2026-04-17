from fastapi import FastAPI
# API 라우터 불러오기
from app.api.v1.symptoms import symptom_router

app = FastAPI(title="AI Taping Guide API", version="1.0.0")

# API 라우터 등록 (공통 URL 접두사 설정)
app.include_router(symptom_router, prefix="/api/v1/symptoms", tags=["Symptoms"])

@app.get("/")
def read_root():
    return {"message": "AI Taping Guide Backend is running!"}