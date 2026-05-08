import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DASHSCOPE_API_KEY: str | None = None
    BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    EMBEDDING_MODEL: str = "text-embedding-v3"
    LLM_MODEL: str = "qwen3.5-plus"

    TOP_K: int = 20
    RERANK_TOP_K: int = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.DASHSCOPE_API_KEY:
            os.environ["OPENAI_API_KEY"] = self.DASHSCOPE_API_KEY


Config = Settings()