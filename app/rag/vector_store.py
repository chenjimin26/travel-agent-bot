import os
from langchain_chroma import Chroma
from app.rag.embeddings import embedding_model


class VectorStore:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DB_PATH = os.path.join(BASE_DIR, "data", "chroma_db")

    def __init__(self, persist_dir: str = None, collection_name: str = "attractions"):
        persist_dir = persist_dir or self.DB_PATH

        self.store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_model,
            persist_directory=persist_dir
        )

    def add_documents(self, docs: list, ids: list = None):
        return self.store.add_documents(docs, ids=ids)

    def add_texts(self, texts: list, metadatas: list = None, ids: list = None):
        return self.store.add_texts(texts, metadatas=metadatas, ids=ids)

    def similarity_search(self, query: str, k: int = 5, filter: dict = None):
        return self.store.similarity_search(query, k=k, filter=filter)

    def similarity_search_with_score(self, query: str, k: int = 5, filter: dict = None):
        return self.store.similarity_search_with_score(query, k=k, filter=filter)

    def as_retriever(self, search_kwargs: dict = None):
        return self.store.as_retriever(search_kwargs=search_kwargs or {"k": 5})