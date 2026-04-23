import json
from typing import Optional, Dict

class TapingRegistryManager:
    def __init__(self, registry_filepath: str = None):
        # 직접 확인한 절대 경로를 넣으세요! (Windows 환경)
        # 예: r"C:\Users\USER\Desktop\AI school 2차\main\feat_backend\taping_registry.json"
        target_path = r"C:\Users\USER\Desktop\AI school 2차\main\feat_backend\taping_registry.json"
        
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                self.registry_data = json.load(f)
            print(f"[SUCCESS] 레지스트리 로드 완료!")
        except Exception as e:
            print(f"[FATAL ERROR] 파일 위치 확인 요망: {target_path} -> {e}")

    def get_asset_urls(self, model_id: str, technique_code: str) -> Dict[str, str]:
        """
        체형 모델 ID와 테이핑 기법 코드를 조합하여 3D 모델 및 비디오 URL을 반환합니다.
        """
        # 조합 키 생성 (예: "3148M_KT_KNEE_LATERAL")
        target_key = f"{model_id}_{technique_code}"
        
        for item in self.registry_data:
            if item["registry_key"] == target_key and item.get("active", True):
                return {
                    "combined_glb_url": item["mesh_file"],
                    "guide_video_url": item["guide_video_url"]
                }
                
        # ⚠️ 매칭되는 에셋이 없을 경우 Fallback 방어 로직
        print(f"[WARNING] 3D 에셋을 찾을 수 없습니다: {target_key}")
        return {
            "combined_glb_url": "https://tapingdata1.blob.core.windows.net/models/default/fallback_model.glb",
            "guide_video_url": ""
        }

# 싱글톤으로 인스턴스화 (다른 파일에서 바로 import해서 사용)
registry_manager = TapingRegistryManager("경로/taping_registry.json")