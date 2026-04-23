import json
from typing import Optional, Dict

class TapingRegistryManager:
    def __init__(self, registry_filepath: str = None):
        # 직접 확인한 절대 경로를 넣으세요! (Windows 환경)
        # 예: r"C:\Users\USER\Desktop\AI_school2\main\feat_backend\taping_registry.json"
        target_path = r"C:\Users\USER\Desktop\AI_school2\main\feat_backend\taping_registry.json"
        
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                self.registry_data = json.load(f)
            print(f"[SUCCESS] 레지스트리 로드 완료!")
        except Exception as e:
            print(f"[FATAL ERROR] 파일 위치 확인 요망: {target_path} -> {e}")

    def get_asset_urls(self, model_id: str, technique_code: str) -> Dict[str, str]:
        # 💡 핵심: 3121M_B 같은 ID에서 _B를 떼어내고 순수 ID(3121M)만 추출
        base_model_id = model_id.split('_')[0]
        
        # 조합할 타겟 키를 여러 버전으로 생성 (혹시 모를 매칭 실패 방지)
        target_keys = [f"{base_model_id}_{technique_code}", f"{model_id}_{technique_code}"]
        
        for item in self.registry_data:
            # item["registry_key"]가 우리가 만든 키 중 하나와 일치하면 성공!
            if item["registry_key"] in target_keys and item.get("active", True):
                return {
                    "combined_glb_url": item["mesh_file"],
                    "guide_video_url": item["guide_video_url"]
                }
                
        # ⚠️ 매칭 실패 시 더 안전한 Fallback
        print(f"[WARNING] 매칭 실패, 검색된 모델 ID(base): {base_model_id}, Tech: {technique_code}")
        return {
            "combined_glb_url": "", 
            "guide_video_url": ""
        }

# 싱글톤으로 인스턴스화 (다른 파일에서 바로 import해서 사용)
registry_manager = TapingRegistryManager("경로/taping_registry.json")