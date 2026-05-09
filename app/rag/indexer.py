import os
from app.rag.chunker import chunk_one_city
from app.rag.vector_store import VectorStore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "attractions")


def index_all_cities(data_dir: str = None):
    data_dir = data_dir or DATA_DIR

    store = VectorStore()

    city_files = [f[:-5] for f in os.listdir(data_dir) if f.endswith('.json')]
    total = len(city_files)

    for i, city_name in enumerate(city_files, 1):
        print(f"[{i}/{total}] indexing: {city_name}")

        docs = chunk_one_city(city_name, data_dir)
        if not docs:
            print(f"  skip: no data")
            continue

        ids = [doc.metadata.get('attraction_id', f"{city_name}_{j}")
               for j, doc in enumerate(docs)]
        texts = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]

        store.add_texts(texts, metadatas=metadatas, ids=ids)

        print(f"  done: {len(docs)} attractions")

    print(f"index complete: {total} cities")


if __name__ == "__main__":
    index_all_cities()
