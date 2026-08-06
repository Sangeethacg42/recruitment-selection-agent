import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

class Config:
    """Application Configuration Settings."""
    
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    DEFAULT_PORT: int = int(os.getenv("PORT", "7860"))
    DEFAULT_HOST: str = os.getenv("HOST", "127.0.0.1")
    
    # Graph execution constants
    MAX_REFLECTION_LOOPS: int = 2
    MIN_PASSING_SCORE: int = 80

config = Config()
