import json
from app.llm.qwen_client import llm
from app.config import Config


class Reranker:
    def rerank(self, query: str, docs: list, top_k: int = None):
        try:
            from langchain_core.documents import Document
            is_documents = docs and isinstance(docs[0], Document)
        except:
            is_documents = False

        if top_k is None:
            top_k = Config.RERANK_TOP_K

        if len(docs) <= top_k:
            return docs

        candidates = docs[:top_k * Config.CANDIDATE_POOL_MULTIPLIER]

        docs_text = ""
        for i, doc in enumerate(candidates, 1):
            text = doc.page_content if is_documents else doc.get("content", str(doc))
            docs_text += f"[{i}] {text[:200]}\n"

        try:
            response = llm.invoke([
                {"role": "user", "content": f"""从以下文档中选出与问题最相关的{top_k}篇，返回编号 JSON：
问题：{query}

文档列表：
{docs_text}

请只输出 JSON：{{"top": [编号1, 编号2, ...]}}，按相关性降序。"""}
            ])
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                data = json.loads(response[start:end])
                indices = data.get('top', [])
            else:
                indices = list(range(1, len(candidates) + 1))

            scored = []
            seen = set()
            for idx in indices:
                try:
                    i = int(idx) - 1
                    if 0 <= i < len(candidates) and i not in seen:
                        seen.add(i)
                        scored.append(candidates[i])
                except:
                    pass
            for i, doc in enumerate(candidates):
                if i not in seen:
                    scored.append(doc)
            return scored[:top_k]
        except:
            return candidates[:top_k]