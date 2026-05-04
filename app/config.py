from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    model_name: str = "gpt-4o-mini"

    database_url: str = "clinica_bot.sqlite"
    docs_dir: str = "docs"

    # Meta WhatsApp Cloud API
    meta_access_token: str
    meta_phone_number_id: str
    meta_webhook_verify_token: str = "clinica-bot-verify"
    meta_app_secret: str = ""
    meta_api_version: str = "v20.0"

    class Config:
        env_file = ".env"


settings = Settings()
