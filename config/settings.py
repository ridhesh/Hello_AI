from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str = "sk-not-set"
    gemini_api_key: str
    redis_url: str
    database_url: str
    api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
