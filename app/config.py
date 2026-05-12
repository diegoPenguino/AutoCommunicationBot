from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    telegram_bot_token: str = ""
    telegram_group_id: str = ""
    openai_api_key: str = ""
    gmail_address: str = ""
    gmail_app_password: str = ""
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_target_group_id: str = ""
    webhook_url: str = ""
    admin_user_id: int = 0  # To ensure only you can trigger broadcasts
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/autonotifications"

    class Config:
        env_file = ".env"

settings = Settings()
