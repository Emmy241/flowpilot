from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openrouter_api_key: str
    database_url: str = ""
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080

    class Config:
        env_file = ".env"

settings = Settings()
