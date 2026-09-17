"""Typed settings loaded from .env — see .env.example for all options."""
from functools import lru_cache
from typing import Dict, List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_models: str = "llama3.1,mistral,phi3"

    # OpenAI
    openai_api_key: str = ""
    openai_models: str = "gpt-4o-mini"

    # Judge
    judge_provider: str = "ollama"
    judge_model: str = "llama3.1"

    # Pricing (USD per 1K tokens) — extend this dict as more paid models are added.
    openai_gpt4o_mini_input_cost: float = 0.00015
    openai_gpt4o_mini_output_cost: float = 0.0006

    # App
    app_env: str = "development"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    database_url: str = "sqlite:///./arena.db"
    battle_timeout_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def ollama_model_list(self) -> List[str]:
        return [m.strip() for m in self.ollama_models.split(",") if m.strip()]

    @property
    def openai_model_list(self) -> List[str]:
        return [m.strip() for m in self.openai_models.split(",") if m.strip()]

    @property
    def pricing_table(self) -> Dict[str, Dict[str, float]]:
        """Maps model_id -> {'input': $/1K tokens, 'output': $/1K tokens}."""
        return {
            "gpt-4o-mini": {
                "input": self.openai_gpt4o_mini_input_cost,
                "output": self.openai_gpt4o_mini_output_cost,
            },
            # Every Ollama model is free (self-hosted) — see evaluator.estimate_cost().
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
