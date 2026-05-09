from langchain_core.documents import Document
from app.rag.vector_store import VectorStore
from app.llm.qwen_client import llm
from app.config import Config


class Retriever:
    def __init__(self):
        self.store = VectorStore()

    def search(self, query: str, k: int = None):
        if k is None:
            k = Config.TOP_K
        return self.store.similarity_search_with_score(query, k=k)

    def search_expanded(self, query: str, k: int = None, enable_mqe: bool = None,
                        enable_hyde: bool = None, pool_multiplier: int = None):
        if k is None:
            k = Config.TOP_K
        if enable_mqe is None:
            enable_mqe = Config.ENABLE_MQE
        if enable_hyde is None:
            enable_hyde = Config.ENABLE_HYDE
        if pool_multiplier is None:
            pool_multiplier = Config.SEARCH_POOL_MULTIPLIER

        queries = [query]

        if enable_mqe:
            mqe = self._generate_mqe(query, n=Config.MQE_EXPANSIONS)
            queries.extend(mqe)

        if enable_hyde:
            hyde_text = self._generate_hyde(query)
            if hyde_text:
                queries.append(hyde_text)

        queries = list(dict.fromkeys(queries))
        pool = max(k * pool_multiplier, Config.MIN_POOL_SIZE)
        per_q = max(1, pool // len(queries))

        merged = {}
        for q in queries:
            hits = self.store.similarity_search_with_score(q, k=per_q)
            for doc, score in hits:
                key = doc.page_content.strip()
                if key not in merged or score < merged[key][1]:
                    merged[key] = (doc, score)

        sorted_docs = sorted(merged.values(), key=lambda x: x[1])
        return [doc for doc, _ in sorted_docs[:k]]

    def _generate_mqe(self, query: str, n: int = 2):
        try:
            messages = [
                {"role": "system", "content": "你是检索查询扩展助手。生成语义等价或互补的多样化查询。使用中文，简短，避免标点。"},
                {"role": "user", "content": f"原始查询：{query}\n请给出{n}个不同表述的查询，每行一个。"}
            ]
            text = llm.invoke(messages)
            lines = [ln.strip("- \t") for ln in (text or "").splitlines()]
            return [ln for ln in lines if ln][:n]
        except:
            return []

    def _generate_hyde(self, query: str):
        try:
            messages = [
                {"role": "system", "content": "根据用户问题，先写一段可能的答案性段落，用于向量检索。直接写段落，不要分析过程。"},
                {"role": "user", "content": f"问题：{query}\n请直接写一段中等长度、客观、包含关键术语的段落。"}
            ]
            return llm.invoke(messages)
        except:
            return None