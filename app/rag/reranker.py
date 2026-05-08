from app.llm.qwen_client import QwenClient
from sentence_transformers import CrossEncoder

from app import config


class Reranker:
    def __init__(self):
        self.llm = QwenClient()
    
    def rerank(self, query: str, results: dict, top_k: int = config.Config.RERANK_TOP_K) -> list:
        if not results or not results.get('documents'):
            return []
        
        docs = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        if len(docs) <= top_k:
            return self._format_results(docs, metadatas)
        
        scored = []
        for doc, meta in zip(docs[:top_k * 4], metadatas[:top_k * 4]):
            score = self._score(query, doc)
            scored.append((score, doc, meta))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        top_results = scored[:top_k]
        return self._format_results([t[1] for t in top_results], [t[2] for t in top_results])
    
    def rerank_cross(self, query: str, results: dict, top_k: int = config.Config.RERANK_TOP_K) -> list:
        if not results or not results.get('documents'):
            return []
        
        docs = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        if len(docs) <= top_k:
            return self._format_results(docs, metadatas)
        

        model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        pairs = [[query, doc] for doc in docs[:top_k * 4]]
        scores = model.predict(pairs)
        
        scored = list(zip(scores, docs[:top_k * 4], metadatas[:top_k * 4]))
        scored.sort(key=lambda x: x[0], reverse=True)
        
        top_results = scored[:top_k]
        return self._format_results([t[1] for t in top_results], [t[2] for t in top_results])


    def _score(self, query: str, doc: str) -> float:
        prompt = f"""请判断下面文档和问题相关程度，打分 0-10：
问题：{query}
文档：{doc}
请直接输出数字分数，不要其他内容："""
        try:
            response = self.llm.chat(prompt)
            score = float(response.strip())
            return min(max(score, 0), 10)
        except:
            return 5.0
    
    def _format_results(self, docs: list, metadatas: list) -> list:
        results = []
        for i, (doc, meta) in enumerate(zip(docs, metadatas), 1):
            results.append({
                "rank": i,
                "content": doc,
                "metadata": meta
            })
        return results