from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # LLM/AI configuration
    AI_MODEL: Optional[str] = "gpt-4o"
    LLM_CLIENT: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_API_VERSION: Optional[str] = None
    ENABLE_AGENT: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()