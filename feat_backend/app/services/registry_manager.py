# app/services/registry_manager.py
import json
import logging
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class TapingRegistryManager:
    def __init__(self, registry_filepath: Optional[str] = None):
        # 🌟 [1번 해결] 파일 위치 기준 상대 경로 자동 설정
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.target_path = registry_filepath or (BASE_DIR / "taping_registry.json")
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
                                "guide_video_url": item.get("guide_video_url", ""),
                                "base_body_id": key.split('_')[0] 
                            }
            logger.info(f"[SUCCESS] 레지스트리 로드 완료: {self.target_path}")
        except Exception as e:
            logger.error(f"[FATAL ERROR] 레지스트리 로드 실패: {e}")

    def get_asset_urls(self, model_id: str, technique_code: str) -> Dict[str, str]:
        combined_key = f"{model_id}_{technique_code}"
        if combined_key in self.registry_map:
            return self.registry_map[combined_key]
        for key, value in self.registry_map.items():
            if technique_code in key:
                return value
        return {}

# 🌟 다른 파일에서 바로 쓸 수 있도록 인스턴스 생성
registry_manager = TapingRegistryManager()