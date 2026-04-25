# app/services/cv_module.py
import sys
from pathlib import Path
from fastapi.concurrency import run_in_threadpool

# feat_cv 폴더 경로를 시스템에 추가 (실제 모듈 임포트용)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CV_PATH = PROJECT_ROOT / "feat_cv"
if str(CV_PATH) not in sys.path:
    sys.path.insert(0, str(CV_PATH))

try:
    from cv import run_body_search_safe
    cv_module_loaded = True
except ImportError as e:
    print(f"[WARN] cv 모듈 임포트 실패: {e}")
    run_body_search_safe = None
    cv_module_loaded = False


class BodyAnalyzer:
    def __init__(self):
        print("[LOG] CV Module 초기화 완료 (실제 CV 연동 모드)")

    async def analyze_image(self, image_path: str, height: float, weight: float, gender: str, privacy_opt_out: bool = False):
        """
        실제 호진님의 CV 파이프라인을 호출하고, 
        매칭 실패 또는 모듈 에러 시 기본 모델(JerryPing)을 반환합니다.
        """
        try:
            if not cv_module_loaded:
                raise ImportError("CV 모듈을 찾을 수 없습니다.")

            # 1. 실제 CV 모듈 실행 (비동기 환경에서 블로킹 방지를 위해 쓰레드풀 사용)
            raw_cv_result = await run_in_threadpool(
                run_body_search_safe,
                image_path=image_path,
                height_cm=height,
                weight_kg=weight,
                sex=gender,
                privacy_opt_out=privacy_opt_out
            )

            # 2. 결과 추출 및 Fallback 처리 (핵심: JerryPing 보장)
            best_match = raw_cv_result.get("best_match") or {}
            matched_model_id = best_match.get("model_id", "JerryPing")
            shape_score = raw_cv_result.get("shape_score", 0.0)
            bmi_group = raw_cv_result.get("bmi_group", "normal")

        except Exception as e:
            print(f"[ERROR] CV 분석 실패, 기본 모델(JerryPing)로 대체합니다. 원인: {e}")
            matched_model_id = "JerryPing"
            shape_score = 0.0
            bmi_group = "unknown"

        # 3. 라우터(body.py)로 넘길 정제된 응답 포맷 구성
        refined_result = {
            "matched_model_id": matched_model_id,
            "shape_score": shape_score,
            "metrics": {
                "bmi_group": bmi_group
            }
        }

        return refined_result

# 전역 싱글톤 인스턴스 (라우터에서 쉽게 가져다 쓸 수 있도록)
body_analyzer = BodyAnalyzer()