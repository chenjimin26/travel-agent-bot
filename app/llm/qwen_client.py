from openai import OpenAI
from app.config import Config
import json, os, time, threading

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
_log_lock = threading.Lock()


def _agent_name(messages: list) -> str:
    """根据 system prompt 关键词识别 Agent"""
    if not messages or messages[0].get("role") != "system":
        return "unknown"
    text = messages[0]["content"]
    keywords = [
        ("旅行规划总指挥", "Supervisor"),
        ("出行交通助手", "Transport"),
        ("旅行攻略提取助手", "Guide"),
        ("检索查询扩展助手", "Retriever-MQE"),
        ("假设文档", "Retriever-HyDE"),
        ("酒店推荐助手", "Hotel"),
        ("旅行行程规划师", "Planner"),
        ("旅行方案审核员", "Evaluator"),
        ("旅行攻略文案师", "Writer"),
        ("旅行助手", "Chat"),
    ]
    for kw, name in keywords:
        if kw in text:
            return name
    return "unknown"


def _log_call(model: str, messages: list, response: str, duration: float):
    record = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "agent": _agent_name(messages),
        "model": model,
        "prompt_chars": sum(len(m.get("content", "")) for m in messages),
        "response_chars": len(response or ""),
        "duration_s": round(duration, 1),
        "response_preview": (response or "")[:200]
    }
    log_file = os.path.join(LOG_DIR, f"{time.strftime('%Y-%m-%d')}.jsonl")
    with _log_lock:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


class QwenLLM:
    def __init__(self, model: str = None):
        self.client = OpenAI(
            api_key=Config.DASHSCOPE_API_KEY,
            base_url=Config.BASE_URL
        )
        self.model = model or Config.LLM_MODEL

    def invoke(self, messages: list) -> str:
        t0 = time.time()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        result = response.choices[0].message.content
        _log_call(self.model, messages, result, time.time() - t0)
        return result


def get_llm(model_key: str = None):
    """按注册表 key 获取 LLM 实例。model_key 可以是 'qwen-flash' / 'kimi' / 'deepseek' 等。"""
    if model_key and model_key in Config.MODEL_REGISTRY:
        model = Config.MODEL_REGISTRY[model_key]
    else:
        model = model_key or Config.LLM_MODEL
    return QwenLLM(model=model)


# 默认实例，兼容旧代码
llm = get_llm()