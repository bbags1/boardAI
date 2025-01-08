from pydantic_settings import BaseSettings
from typing import Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "BoardAI"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "2%@ujeu7!axr@m@kwq*b*xy354x%dq(ol*fpt61+1rb3+&yu&e")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days

    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "boardai")
    
    # AI Personalities Default Templates
    DEFAULT_PERSONALITIES: Dict = {
        "legal": {
            "name": "Legal Advisor",
            "description": "Expert in corporate law and regulations",
            "prompt_template": "As a legal advisor with expertise in corporate law, analyze this: {input}"
        },
        "financial": {
            "name": "Financial Advisor",
            "description": "Expert in corporate finance and strategy",
            "prompt_template": "As a financial advisor with expertise in corporate finance, analyze this: {input}"
        },
        "technology": {
            "name": "Technology Advisor",
            "description": "Expert in technology and digital transformation",
            "prompt_template": "As a technology advisor with expertise in digital transformation, analyze this: {input}"
        }
    }

    class Config:
        case_sensitive = True

settings = Settings()