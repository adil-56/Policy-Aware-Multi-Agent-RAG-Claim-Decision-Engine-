from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Policy-Aware Multi-Agent RAG Claim Decision Engine"
    API_V1_STR: str = "/api/v1"
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    DEFAULT_MODEL_NAME: str = "gpt-4-turbo-preview"
    
    # Vector DB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # Reranker
    RERANKER_MODEL_NAME: str = "BAAI/bge-reranker-base"
    
    # Paths
    POLICY_DOCUMENT_PATH: str = "./data/policy.pdf"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
