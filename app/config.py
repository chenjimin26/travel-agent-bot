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

    # ── API ──
    DASHSCOPE_API_KEY: str | None = None
    BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    MT_HOTEL_API_KEY: str | None = None

    # ── Model ──
    EMBEDDING_MODEL: str = "text-embedding-v3"
    LLM_MODEL: str = "qwen3.6-flash-2026-04-16"

    # ── Model Registry ──
    MODEL_REGISTRY: dict = {
        "qwen-flash": "qwen3.6-flash-2026-04-16",
        "qwen-plus": "qwen3.6-plus",
        "glm": "glm-5.1",
        "kimi": "kimi-k2.6",
        "minimax": "MiniMax-M2.5",
        "deepseek": "deepseek-v4-pro",
    }

    # ── Retrieval ──
    TOP_K: int = 10
    RERANK_TOP_K: int = 5
    CANDIDATE_POOL_MULTIPLIER: int = 2
    SEARCH_POOL_MULTIPLIER: int = 3
    MIN_POOL_SIZE: int = 15

    # ── MQE / HyDE / Rerank ──
    ENABLE_MQE: bool = True
    ENABLE_RERANK: bool = True
    MQE_EXPANSIONS: int = 2
    ENABLE_HYDE: bool = True

    # ── Query Modes ──
    FAST_POOL_MULTIPLIER: int = 1
    PRECISION_POOL_MULTIPLIER: int = 3

    # ── Memory ──
    MEMORY_MAX_SIZE: int = 5

    # ── System Prompt ──
    SYSTEM_PROMPT: str = """你是旅游助手。严格按以下格式回答，每条景区信息必须完整独立：

### 景区名
- 推荐理由：一句话描述
- 门票：价格
- 开放时间：时段

规则：
1. 每个景区以 ### 开头，后面必须有一个空格再写名称
2. 景区之间必须空一行
3. 推荐理由、门票、开放时间各占一行，用 - 开头
4. 门票价格紧跟在冒号后面，如「门票：15元」
5. 不要把所有景区信息堆在一行"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.DASHSCOPE_API_KEY:
            os.environ["OPENAI_API_KEY"] = self.DASHSCOPE_API_KEY


Config = Settings()