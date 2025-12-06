from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="local-llm-backend", description="Service name")
    host: str = Field(default="0.0.0.0", description="Bind address")
    port: int = Field(default=8000, description="Bind port")
    ollama_model: str = Field(default="llama3", description="Default Ollama model name")
    ollama_api_url: str | None = Field(
        default=None, description="Override Ollama base URL (e.g. http://localhost:11434)"
    )

    class Config:
        env_prefix = "APP_"
        env_file = ".env"


settings = Settings()
