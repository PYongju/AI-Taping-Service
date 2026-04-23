# seed_registry.py
import json
from app.services.db_manager import db

def load_seed_data():
    # 1. 다운받은 JSON 파일 읽기
    with open("taping_registry.json", "r", encoding="utf-8") as file:
        registry_data = json.load(file)
    
    # 2. Cosmos DB에 하나씩 Insert (id 필드가 없으면 registry_key를 id로 사용)
    for item in registry_data:
        if "id" not in item:
            item["id"] = item["registry_key"] # Cosmos DB는 항상 'id' 필드가 필수입니다.
            
        try:
            db.registry_container.upsert_item(body=item)
            print(f"[SUCCESS] Inserted: {item['id']}")
        except Exception as e:
            print(f"[ERROR] Failed to insert {item['id']}: {e}")

if __name__ == "__main__":
    load_seed_data()
    print("모든 레지스트리 데이터 적재 완료!")