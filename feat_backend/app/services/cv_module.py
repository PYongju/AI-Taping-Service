# app/services/cv_module.py

import sys
# TODO: 호진님의 CV 폴더 구조에 맞게 임포트 경로 수정 (월요일 연동 시)
# from feat_cv.cv import run_body_search 

class BodyAnalyzer:
    def __init__(self):
        # MediaPipe 모델 등 초기화 로직
        print("[LOG] CV Module 초기화 완료 (백엔드 어댑터 대기 중)")

    async def analyze_image(self, image_bytes: bytes, height: float, weight: float, gender: str):
        """
        메모리의 이미지 바이트 데이터를 호진님의 CV 모듈로 전달하고,
        백엔드 스키마에 맞게 정제하여 반환하는 어댑터 함수
        """
        try:
            # --------------------------------------------------
            # 1. 호진님의 실제 CV 모듈 호출 (월요일 통합 시 주석 해제)
            # --------------------------------------------------
            # raw_cv_result = run_body_search(
            #     image_bytes=image_bytes, 
            #     height=height, 
            #     weight=weight, 
            #     gender=gender
            # )
            
            # [임시 Mock - 월요일 통합 전까지 프론트엔드 테스트용으로 유지]
            raw_cv_result = {
                "matched_model_id": "3148M" if gender == "male" else "7036F",
                "shape_score": 0.95,       # 호진님이 계산해준 유사도 점수
                "bmi_group": "normal",     # 비즈니스 로직용 데이터
                "shoulder_width": 40.5,    # (로깅/디버깅용 Raw 데이터)
                "hip_width": 38.2
            }

            # --------------------------------------------------
            # 2. 결과값 정제 (백엔드 Pydantic 스키마 및 DB 최적화)
            # --------------------------------------------------
            # DB 비용 절감을 위해 skeleton, width 등의 Raw 데이터는 여기서 버리고(또는 별도 로깅)
            # 프론트와 합의된 필수 비즈니스 데이터만 라우터(body.py)로 넘깁니다.
            
            refined_result = {
                "matched_model_id": raw_cv_result.get("matched_model_id", "3148M"),
                "shape_score": raw_cv_result.get("shape_score", 0.95),
                "metrics": {
                    "bmi_group": raw_cv_result.get("bmi_group", "normal")
                }
            }
            
            return refined_result

        except Exception as e:
            print(f"[CV Module Error] 체형 분석 중 오류 발생: {str(e)}")
            # 에러 발생 시 라우터가 500 에러로 캐치할 수 있도록 예외를 던짐
            raise ValueError(f"MediaPipe 체형 분석 실패: {str(e)}")

# 외부에서 가져다 쓸 수 있도록 인스턴스 생성
body_analyzer = BodyAnalyzer()