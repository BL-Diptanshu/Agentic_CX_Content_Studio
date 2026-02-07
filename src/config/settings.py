from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Dict, Any, Optional
import os

class Settings(BaseSettings):
    """
    Centralized configuration management.
    Loads from .env file and environment variables.
    """
    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    STATIC_DIR: Path = BASE_DIR / "static"
    LOG_CONFIG_PATH: Path = BASE_DIR / "config" / "logging.config.yaml"
    MODEL_CONFIG_PATH: Path = BASE_DIR / "config" / "model.config.yaml"
    
    # API Keys
    GROQ_API_KEY: Optional[str] = None
    HUGGINGFACE_API_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Model Configs
    DEFAULT_LLM_MODEL: str = "llama-3.1-8b-instant"
    DEFAULT_IMAGE_MODEL: str = "stabilityai/stable-diffusion-xl-base-1.0"
    
    # RAG Configs
    RAG_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    RAG_INDEX_PATH: Path = DATA_DIR / "vectordb" / "faiss" / "brand_index.bin"
    RAG_DOCS_PATH: Path = DATA_DIR / "vectordb" / "faiss" / "brand_docs.pkl"
    BRAND_KB_PATH: Path = BASE_DIR / "brand_kb"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars

# Global settings instance
settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(exist_ok=True, parents=True)
settings.STATIC_DIR.mkdir(exist_ok=True, parents=True)
(settings.DATA_DIR / "vectordb" / "faiss").mkdir(exist_ok=True, parents=True)

if __name__ == "__main__":
    print(f"Base Dir: {settings.BASE_DIR}")
    print(f"Index Path: {settings.RAG_INDEX_PATH}")
