from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.db_manager import db

router = APIRouter()

# 프론트엔드에서 보내는 데이터 구조에 맞게 스키마 정의
class SaveRequest(BaseModel):
    session_id: str
    taping_id: str

@router.post("/save")
async def save_session_record(request: SaveRequest):
    try:
        # DB 매니저를 통해 해당 세션을 '저장됨' 상태로 변경하거나 기록 테이블로 이동
        # db.save_session_record는 사용 중인 db_manager의 메서드 이름에 맞춰 수정하세요.
        success = db.update_session(request.session_id, {"is_saved": True}) 
        
        if not success:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
            
        return {"status": "success", "message": "기록이 저장되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))