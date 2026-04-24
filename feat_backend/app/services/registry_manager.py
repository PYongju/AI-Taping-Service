import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class TapingRegistryManager:
    def __init__(self, registry_filepath: Optional[str] = None):
        self.target_path = registry_filepath or r"C:\Users\USER\Desktop\AI_school2\main\feat_backend\taping_registry.json"
        self.registry_map = {}
        self._load_registry()

    def _load_registry(self):
        try:
            with open(self.target_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if item.get("active", True):
                        key = item.get("registry_key")
                        if key:
                            self.registry_map[key] = {
                                "combined_glb_url": item.get("mesh_file", ""),
                                "guide_video_url": item.get("guide_video_url", "")
                            }
            logger.info(f"[SUCCESS] 레지스트리 인덱싱 완료 ({len(self.registry_map)}개 항목)")
        except Exception as e:
            logger.error(f"[FATAL ERROR] 레지스트리 로드 실패: {e}")

    def get_asset_urls(self, model_id: str, technique_code: str) -> Dict[str, str]:
        # 1. 기술 코드 자체가 곧 전체 키인 경우 (3148M_...)
        if technique_code in self.registry_map:
            return self.registry_map[technique_code]
            
        # 2. 조합 키 시도 (model_id_technique)
        combined_key = f"{model_id}_{technique_code}"
        if combined_key in self.registry_map:
            return self.registry_map[combined_key]
            
        logger.warning(f"[WARNING] 매칭 실패! 키: {technique_code} 또는 {combined_key}")
        return {"combined_glb_url": "", "guide_video_url": ""}

registry_manager = TapingRegistryManager()