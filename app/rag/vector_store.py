import os
import chromadb


class VectorStore:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DB_PATH = os.path.join(BASE_DIR, "data", "chroma_db")
    
    def __init__(self, persist_dir: str = None, collection_name: str = "attractions"):
        persist_dir = persist_dir or self.DB_PATH
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(collection_name)

    def add(self, documents: list, embeddings: list, metadatas: list, ids: list):
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query: str, top_k: int = 5, where_filter: dict = None) -> dict:
        return self.collection.query(query_texts=[query], n_results=top_k, where=where_filter)
    
    def search_by_embedding(self, query_embedding: list, top_k: int = 5, where_filter: dict = None) -> dict:
        return self.collection.query(query_embeddings=[query_embedding], n_results=top_k, where=where_filter)