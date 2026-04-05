"""Application settings loaded from environment variables or a .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ALPACA_API_KEY: str
    ALPACA_SECRET_KEY: str
    PAPER_TRADING: bool = True
    WEBHOOK_SECRET: str
    MAX_ORDER_QTY: int = 100
    MAX_DAILY_ORDERS: int = 20
    RISK_CHECK_TIMEOUT_SECONDS: int = 8
    ORDER_SUBMIT_TIMEOUT_SECONDS: int = 12


settings = Settings()
