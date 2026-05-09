from typing import List
from openai import OpenAI
from langchain_core.embeddings import Embeddings
from app.config import Config


class TongyiEmbeddings(Embeddings):
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.DASHSCOPE_API_KEY,
            base_url=Config.BASE_URL
        )
        self.model = Config.EMBEDDING_MODEL

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding


embedding_model = TongyiEmbeddings()