from pydantic import BaseModel
from typing import Optional, List
from datetime import timedelta

class Settings(BaseModel):
    # OpenAI API settings
    OPENAI_API_KEY: Optional[str] = None
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./fragrance_chatbot.db"
    
    # Application settings
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Fragrance Chatbot API"
    PROJECT_DESCRIPTION: str = "API for the Fragrance Chatbot application"
    VERSION: str = "1.0.0"
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Session settings
    SESSION_TIMEOUT: timedelta = timedelta(hours=24)
    CLEANUP_INTERVAL: timedelta = timedelta(hours=1)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 