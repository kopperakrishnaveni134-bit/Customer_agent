from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RecallDesk"
    app_env: str = "development"

    database_url: str = "sqlite:///./recalldesk.db"

    hindsight_api_url: str
    hindsight_api_key: str
    hindsight_bank_id: str = "recalldesk"

    groq_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()