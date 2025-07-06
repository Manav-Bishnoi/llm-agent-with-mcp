from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_URL: str = "http://localhost:11434"
    MAX_CONTEXT_SIZE: int = 1000
    CONTEXT_EXPIRY_HOURS: int = 24
    DEFAULT_TIMEOUT: int = 30
    LOG_LEVEL: str = "INFO"
    class Config:
        env_file = ".env"

settings = Settings()
