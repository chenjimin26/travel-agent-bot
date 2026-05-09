from app.rag.retriever import Retriever
from app.rag.reranker import Reranker
from app.llm.qwen_client import QwenClient
from app.memory.memory import Memory
from app.config import Config


def main():
    retriever = Retriever()
    reranker = Reranker()
    llm = QwenClient()
    memory = Memory()

    print("=== 旅游 RAG 助手 ===")
    print("输入 'quit' 退出\n")

    while True:
        query = input("你: ").strip()
        if not query:
            continue
        if query.lower() in ['quit', 'q', '退出']:
            print("再见！")
            break

        results = retriever.search(query, top_k=Config.TOP_K)
        reranked = reranker.rerank_cross(query, results, top_k=Config.RERANK_TOP_K)

        context = "\n".join([
            f"- {r['content']}" for r in reranked
        ])

        history_text = memory.format_history()

        print("\n助手: ", end='')
        full_answer = ""
        for chunk in llm.chat_stream([{"role": "user", "content": history_text + "\n参考信息：\n" + context + "\n\n问题：" + query}]):
            full_answer += chunk
        print("\n")

        memory.add(query, full_answer)


if __name__ == "__main__":
    main()