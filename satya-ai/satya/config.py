from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration settings for Satya AI."""
    satya_agent_keys: str = "DEMO_KEY"
    audit_secret: str = "default_secret"
    database_url: str = "sqlite+aiosqlite:///satya.db"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
