from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_secret: str = "dev-secret"

    anthropic_api_key: str
    model_name: str = "claude-haiku-4-5-20251001"

    database_url: str = "postgresql://bot:bot@localhost:5432/clinica_bot"

    evolution_api_url: str = "http://localhost:8080"
    evolution_api_key: str = ""
    evolution_instance: str = "clinica"

    class Config:
        env_file = ".env"


settings = Settings()
