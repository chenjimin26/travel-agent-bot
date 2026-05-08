import os
from app.rag.chunker import chunk_one_city
from app.rag.embeddings import EmbeddingClient
from app.rag.vector_store import VectorStore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "attractions")


def index_all_cities(data_dir: str = None):
    data_dir = data_dir or DATA_DIR
    
    store = VectorStore()
    embedder = EmbeddingClient()
    
    city_files = [f[:-5] for f in os.listdir(data_dir) if f.endswith('.json')]
    total = len(city_files)
    
    for i, city_name in enumerate(city_files, 1):
        print(f"[{i}/{total}] indexing: {city_name}")
        
        chunks = chunk_one_city(city_name, data_dir)
        if not chunks:
            print(f"  skip: no data")
            continue
        
        documents = [c['content'] for c in chunks]
        metadatas = [c['metadata'] for c in chunks]
        ids = [c['id'] for c in chunks]
        
        all_embeddings = []
        for j in range(0, len(documents), 10):
            docs_batch = documents[j:j+10]
            emb_batch = embedder.embed_batch(docs_batch)
            all_embeddings.extend(emb_batch)
        
        store.add(documents=documents, embeddings=all_embeddings, metadatas=metadatas, ids=ids)
        
        print(f"  done: {len(chunks)} attractions")
    
    print(f"index complete: {total} cities")


if __name__ == "__main__":
    index_all_cities()