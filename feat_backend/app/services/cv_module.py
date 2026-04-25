# app/services/cv_module.py
import sys
from pathlib import Path
from fastapi.concurrency import run_in_threadpool

# feat_cv 폴더 경로를 시스템에 추가
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
        try:
            if not cv_module_loaded:
                raise ImportError("CV 모듈을 찾을 수 없습니다.")

            # 1. 실제 CV 모듈 실행
            raw_cv_result = await run_in_threadpool(
                run_body_search_safe,
                image_path=image_path,
                height_cm=height,
                weight_kg=weight,
                sex=gender,
                privacy_opt_out=privacy_opt_out
            )

            # 2. 결과 추출 및 Fallback 처리
            best_match = raw_cv_result.get("best_match") or {}
            raw_model_id = best_match.get("model_id", "JerryPing")
            
            # 🌟 [핵심 해결책] "3148M_B" 처럼 꼬리가 붙어오면 무조건 앞부분("3148M")만 자릅니다!
            matched_model_id = raw_model_id.split('_')[0] if "_" in raw_model_id else raw_model_id
            
            shape_score = raw_cv_result.get("shape_score", 0.0)
            bmi_group = raw_cv_result.get("bmi_group", "normal")

        except Exception as e:
            print(f"[ERROR] CV 분석 실패, 기본 모델(JerryPing)로 대체합니다. 원인: {e}")
            matched_model_id = "JerryPing"
            shape_score = 0.0
            bmi_group = "unknown"

        # 3. 라우터로 넘길 정제된 응답
        refined_result = {
            "matched_model_id": matched_model_id,
            "shape_score": shape_score,
            "metrics": {
                "bmi_group": bmi_group
            }
        }

        return refined_result

# 전역 싱글톤 인스턴스
body_analyzer = BodyAnalyzer()