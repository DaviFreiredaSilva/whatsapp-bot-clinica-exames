from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str
    model_name: str = "gemini-2.5-flash"

    database_url: str = "clinica_bot.sqlite"
    docs_dir: str = "docs"

    # Z-API
    zapi_instance_id: str = ""
    zapi_token: str = ""
    zapi_client_token: str = ""  # security token enviado pelo Z-API no header Client-Token

    class Config:
        env_file = ".env"


settings = Settings()
