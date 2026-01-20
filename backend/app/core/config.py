""" Configuration management for The Drunken Bot backend. """
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Configuration
    app_name: str = "The Drunken Bot API"
    version: str = "0.0.0"
    debug: bool = False

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8001

    # vLLM configuration
    vllm_url: str = "http://localhost:8000/v1/completions"
    vllm_timeout: float = 30.0
    model_name: str = "Qwen/Qwen3-0.6B"

    # CORS configuration
    allowed_origins: list[str] = [
        "http://localhost:4321",
        "http://localhost:3000",
    ]

    # Completion defaults
    default_max_tokens: int = 20
    default_temperature: float = 0.7
    max_allowed_tokens: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    """ Get cached settings instance. """
    return Settings()