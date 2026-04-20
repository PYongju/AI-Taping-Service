from azure.cosmos import CosmosClient, PartitionKey
from app.core.config import settings

class CosmosDBManager:
    def __init__(self):
        # 1. 클라이언트 연결
        self.client = CosmosClient(settings.COSMOS_ENDPOINT, settings.COSMOS_KEY)
        
        # 2. 데이터베이스 연결 (없으면 생성)
        self.database = self.client.create_database_if_not_exists(id=settings.COSMOS_DATABASE)
        
        # 3. 세션 컨테이너 연결 (파티션 키는 /session_id 로 설정)
        self.session_container = self.database.create_container_if_not_exists(
            id=settings.SESSION_CONTAINER,
            partition_key=PartitionKey(path="/session_id")
        )
        
        # 4. 레지스트리 컨테이너 연결 (파티션 키는 /technique_code 로 설정)
        self.registry_container = self.database.create_container_if_not_exists(
            id=settings.REGISTRY_CONTAINER,
            partition_key=PartitionKey(path="/technique_code")
        )
        print("[LOG] Azure Cosmos DB 연결 완료!")

    def create_session(self, session_data: dict):
        """새로운 세션 문서를 DB에 INSERT 합니다."""
        if "id" not in session_data:
            session_data["id"] = session_data["session_id"]
            
        self.session_container.create_item(body=session_data)
        return session_data
    
    def update_session(self, session_id: str, update_data: dict):
        try:
            # 1. 기존 세션 문서 읽기
            item = self.session_container.read_item(
                item=session_id, 
                partition_key=session_id
            )
            
            # 2. 새로운 데이터로 병합 (Dictionary Update)
            item.update(update_data)
            
            # 3. [핵심] updated_at 자동 갱신 로직 추가
            # 파이프라인의 어느 곳에서 호출하든 항상 최신 시간으로 덮어씌움
            item["updated_at"] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # 4. DB에 최종 저장(Upsert)
            self.session_container.upsert_item(item)
            
            return item
            
        except Exception as e:
            print(f"[DB Error] 세션 업데이트 실패: {str(e)}")
            raise e

    def get_session(self, session_id: str):
        """특정 세션 정보를 가져옵니다."""
        try:
            return self.session_container.read_item(item=session_id, partition_key=session_id)
        except Exception:
            return None

# 싱글톤 패턴처럼 앱 전체에서 db 인스턴스 하나만 재사용합니다.
db = CosmosDBManager()