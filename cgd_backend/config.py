from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    mistral_api_key: str
    allow_origin: str = (
        "http://localhost:8080"  # Default value, used in docker container
    )
    whisper_api_key: str
    production: str = "false"

    model_config = SettingsConfigDict(env_file=".env")
