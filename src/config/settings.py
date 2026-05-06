"""Application settings and configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # vLLM / AMD Configuration
    VLLM_BASE_URL: str = "http://localhost:8000/v1"
    VLLM_API_KEY: str = "not-needed"
    VLLM_MODEL: str = "meta-llama/Llama-3.3-70B-Instruct"

    # Application
    APP_NAME: str = "PeruBank AI Agent"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    APP_PORT: int = 8080
    APP_HOST: str = "0.0.0.0"

    # Agent Configuration
    MAX_AGENT_ITERATIONS: int = 5
    AGENT_TIMEOUT_SECONDS: int = 30
    DEFAULT_TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 4096

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
