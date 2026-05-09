from app.config import Config
from app.llm.qwen_client import llm


class Memory:
    """摘要+缓冲混合记忆：最近 N 轮原样保留，更早的压缩为摘要。"""

    def __init__(self, buffer_size: int = None):
        self.buffer = []
        self.summary = ""
        self.previous_intent = {}
        self.buffer_size = buffer_size if buffer_size is not None else Config.MEMORY_MAX_SIZE

    def add(self, query: str, answer: str):
        self.buffer.append((query, answer))
        if len(self.buffer) > self.buffer_size:
            self._compact()

    def _compact(self):
        overflow = self.buffer[:-self.buffer_size]
        self.buffer = self.buffer[-self.buffer_size:]

        old_text = ""
        for q, a in overflow:
            old_text += f"用户：{q}\n助手：{a[:200]}\n"

        messages = [
            {"role": "system", "content": "你是对话摘要助手。将以下对话压缩为一段简洁的中文摘要，保留关键信息（地名、偏好、约束等）。"},
            {"role": "user", "content": f"现有摘要：{self.summary or '无'}\n\n新对话：\n{old_text}\n\n请输出合并后的摘要（不超过150字）："}
        ]
        try:
            self.summary = llm.invoke(messages)[:300]
        except:
            self.summary = old_text[:300]

    def get_context(self) -> str:
        """返回完整的记忆上下文，供 LLM 拼入 prompt。"""
        parts = []
        if self.summary:
            parts.append(f"历史对话摘要：{self.summary}")
        for q, a in self.buffer:
            parts.append(f"用户：{q}\n助手：{a[:300]}")
        return "\n".join(parts) if parts else ""

    def clear(self):
        self.buffer = []
        self.summary = ""
