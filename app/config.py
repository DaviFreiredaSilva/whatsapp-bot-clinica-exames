from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_secret: str = "dev-secret"

    openai_api_key: str
    model_name: str = "gpt-4o-mini"

    database_url: str = "clinica_bot.sqlite"

    docs_dir: str = "docs"

    evolution_api_url: str = "http://localhost:8080"
    evolution_api_key: str = ""
    evolution_instance: str = "clinica"

    class Config:
        env_file = ".env"


settings = Settings()
