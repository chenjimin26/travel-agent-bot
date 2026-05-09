"""
Retriever Agent — 景点检索

封装现有 RAG 链路（MQE/HyDE/重排序），
返回与目的地和偏好匹配的景点列表。
"""
from app.rag.retriever import Retriever
from app.rag.reranker import Reranker
from app.config import Config


class RetrieverAgent:
    def __init__(self):
        self.retriever = Retriever()
        self.reranker = Reranker()

    def search(self, destination: str, preferences: list[str] = None, top_k: int = None) -> list[dict]:
        if top_k is None:
            top_k = Config.RERANK_TOP_K

        query = destination
        if preferences:
            query = f"{destination} {' '.join(preferences)}"

        docs = self.retriever.search_expanded(
            query,
            k=Config.TOP_K if Config.ENABLE_RERANK else Config.RERANK_TOP_K,
            enable_mqe=Config.ENABLE_MQE,
            enable_hyde=Config.ENABLE_HYDE,
            pool_multiplier=Config.SEARCH_POOL_MULTIPLIER
        )

        if Config.ENABLE_RERANK:
            docs = self.reranker.rerank(query, docs, top_k=top_k)

        results = []
        for doc in docs:
            results.append({
                "name": doc.metadata.get("name", ""),
                "city": doc.metadata.get("city", ""),
                "ticket": doc.metadata.get("ticket", ""),
                "open_time": doc.metadata.get("open_time", ""),
                "best_season": doc.metadata.get("best_season", ""),
                "tags": doc.metadata.get("tags", []),
                "description": doc.page_content[:200]
            })
        return results
