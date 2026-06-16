from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    ANTHROPIC_API_KEY: str
    VOYAGE_API_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    MAX_UPLOAD_SIZE_MB: int = 50
    CHUNK_SIZE_TOKENS: int = 512
    CHUNK_OVERLAP_TOKENS: int = 50
    TOP_K_RETRIEVAL: int = 10
    TOP_K_RERANK: int = 5
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
