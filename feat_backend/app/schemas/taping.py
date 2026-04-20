from pydantic import BaseModel
from typing import List

class TapingRequest(BaseModel):
    session_id: str

class TapingOption(BaseModel):
    option_rank: int        # rank -> option_rank 로 정정
    technique_code: str
    body_region: str        # body_part + region 병존 -> 단일 필드로 통합
    tape_type: str
    why: str                # instruction 분리 (이유)
    anchor_position: str    # instruction 분리 (부착 위치)
    guide_video_url: str
    combined_glb_url: str
    # asset_id는 Registry 내부 처리용으로 스펙에 따라 응답에서 제외

class TapingResponse(BaseModel):
    session_id: str
    status: str
    analysis: str
    options: List[TapingOption]