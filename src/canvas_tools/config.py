import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class Config(BaseModel):
    # Canvas
    canvas_api_url: str = Field(default_factory=lambda: os.getenv("CANVAS_API_URL", ""))
    canvas_api_key: str = Field(default_factory=lambda: os.getenv("CANVAS_API_KEY", ""))

    # Docker
    docker_image: str = Field(default_factory=lambda: os.getenv("DOCKER_IMAGE", "jupyter/scipy-notebook:latest"))
    ollama_docker_image: str = Field(default_factory=lambda: os.getenv("OLLAMA_DOCKER_IMAGE", "ollama/ollama:latest"))
    
    # LLM Providers
    ollama_base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    hf_token: Optional[str] = Field(default_factory=lambda: os.getenv("HF_TOKEN"))

    # Models
    execution_model: str = Field(default_factory=lambda: os.getenv("EXECUTION_MODEL", "qwen2.5-coder:32b")) # Defaulting to a reasonable ollama model name
    execution_provider: str = Field(default_factory=lambda: os.getenv("EXECUTION_PROVIDER", "ollama"))
    
    reviewer_model: str = Field(default_factory=lambda: os.getenv("REVIEWER_MODEL", "claude-3-opus-20240229"))
    reviewer_provider: str = Field(default_factory=lambda: os.getenv("REVIEWER_PROVIDER", "anthropic"))
    
    class Config:
        env_file = ".env"

_config_instance = None

def get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
