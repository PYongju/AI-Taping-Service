# [참고용] Pydantic V2 최신 권장 스타일
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    COSMOS_ENDPOINT: str
    COSMOS_KEY: str
    COSMOS_DATABASE: str = "TapingDB"
    SESSION_CONTAINER: str = "Sessions"
    REGISTRY_CONTAINER: str = "TapingRegistry"
    AZURE_STORAGE_CONNECTION_STRING: str 

    # class Config 대신 model_config를 사용합니다.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()