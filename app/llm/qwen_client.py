from openai import OpenAI
from app.config import Config


class QwenLLM:
    def __init__(self, model: str = None):
        self.client = OpenAI(
            api_key=Config.DASHSCOPE_API_KEY,
            base_url=Config.BASE_URL
        )
        self.model = model or Config.LLM_MODEL

    def invoke(self, messages: list) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content


def get_llm(model_key: str = None):
    """按注册表 key 获取 LLM 实例。model_key 可以是 'qwen-flash' / 'kimi' / 'deepseek' 等。"""
    if model_key and model_key in Config.MODEL_REGISTRY:
        model = Config.MODEL_REGISTRY[model_key]
    else:
        model = model_key or Config.LLM_MODEL
    return QwenLLM(model=model)


# 默认实例，兼容旧代码
llm = get_llm()