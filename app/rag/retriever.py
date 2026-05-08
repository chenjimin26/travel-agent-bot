from app import config
from app.rag.vector_store import VectorStore
from app.rag.embeddings import EmbeddingClient


class Retriever:
    def __init__(self):
        self.store = VectorStore()
        self.embedder = EmbeddingClient()
    
    def search(self, query: str, top_k: int = config.Config.TOP_K, where_filter: dict = None):
        query_embedding = self.embedder.embed_text(query)
        results = self.store.search_by_embedding(query_embedding, top_k, where_filter)
        return results
    
    def format_results(self, results: dict) -> str:
        formatted = []
        docs = results.get('documents', [[]])[0]
        metas = results.get('metadatas', [[]])[0]
        
        for i, (doc, meta) in enumerate(zip(docs, metas), 1):
            formatted.append(f"[{i}] {meta.get('name', '')} ({meta.get('city', '')})")
            formatted.append(f"    {doc}\n")
        
        return "\n".join(formatted)