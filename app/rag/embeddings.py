from openai import OpenAI
from app.config import Config


class EmbeddingClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.DASHSCOPE_API_KEY,
            base_url=Config.BASE_URL
        )
        self.model = Config.EMBEDDING_MODEL

    def embed_text(self, text: str) -> list[float]:
        """获取文本的向量表示"""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量获取向量"""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]
