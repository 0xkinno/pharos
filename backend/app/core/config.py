"""
PHAROS Backend Configuration
Loads settings from environment variables / .env file.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # IBM watsonx.ai
    watsonx_api_key: Optional[str] = None
    watsonx_project_id: Optional[str] = None
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"

    # Model IDs — override via env vars if your region has a different catalog
    # EU-DE region uses: meta-llama/llama-3-3-70b-instruct for instruct tasks
    # US-South region uses: ibm/granite-3-1-8b-instruct
    granite_instruct_model: str = "ibm/granite-3-1-8b-instruct"
    granite_embedding_model: str = "ibm/granite-embedding-278m-multilingual"
    granite_guardian_model: str = "ibm/granite-guardian-3-8b"
    # Fallback instruct model used if primary is unavailable in current region
    llama_instruct_model: str = "meta-llama/llama-3-3-70b-instruct"

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    # Cache
    celestrak_cache_ttl_seconds: int = 3600

    # Paths (resolved relative to project root at runtime)
    standards_index_path: str = "standards/index/chunks.json"
    rules_registry_path: str = "rules/rules_registry.yaml"
    demo_data_path: str = "data/demo/demo_report.json"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def watsonx_configured(self) -> bool:
        return bool(self.watsonx_api_key and self.watsonx_project_id)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
