from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_url: str | None = None
    llm_model: str = "mistral"
    forecast_api_key: str = ":)"
    forecast_detail: bool = True
    forecast_metric: bool = True

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
