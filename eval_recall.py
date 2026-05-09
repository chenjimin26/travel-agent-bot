"""
召回率评估脚本

从 Chroma 随机抽取 N 个景点作为 ground truth，
用景点所属城市+标签生成查询，检查目标景点是否在 top-K 结果中。
"""
import random
import time
from app.rag.retriever import Retriever
from app.rag.vector_store import VectorStore
from app.config import Config


def pick_random_attractions(n=50):
    """从 Chroma 随机抽 N 个景点作为 ground truth"""
    store = VectorStore()
    all_docs = store.store.get()
    indices = random.sample(range(len(all_docs['ids'])), min(n, len(all_docs['ids'])))
    
    samples = []
    for i in indices:
        doc = all_docs['documents'][i]
        meta = all_docs['metadatas'][i]
        samples.append({"content": doc, "metadata": meta})
    return samples


def build_query(attraction):
    """根据景点信息生成检索查询"""
    name = attraction['metadata'].get('name', '')
    city = attraction['metadata'].get('city', '')
    tags = attraction['metadata'].get('tags', [])
    tag = random.choice(tags) if tags else '景点'
    return f"{city}{tag}"


def evaluate(retriever, samples, k=5, enable_mqe=False, enable_hyde=False):
    """计算 recall@k 和 MRR"""
    hits = 0
    reciprocal_ranks = []
    
    for i, sample in enumerate(samples):
        query = build_query(sample)
        target_name = sample['metadata'].get('name', '')
        
        docs = retriever.search_expanded(query, k=k, enable_mqe=enable_mqe, enable_hyde=enable_hyde)
        
        # 检查目标是否在结果中
        found = False
        for rank, doc in enumerate(docs, 1):
            if doc.metadata.get('name', '') == target_name:
                found = True
                reciprocal_ranks.append(1.0 / rank)
                break
        
        if found:
            hits += 1
        
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(samples)}...", end=" ", flush=True)
    
    recall = hits / len(samples)
    mrr = sum(reciprocal_ranks) / len(samples) if reciprocal_ranks else 0.0
    return recall, mrr


def main():
    print(f"模型: {Config.LLM_MODEL} | TOP_K={Config.TOP_K} | RERANK_TOP_K={Config.RERANK_TOP_K}")
    print()
    
    print("抽取测试样本...")
    samples = pick_random_attractions(50)
    print(f"抽取 {len(samples)} 个景点\n")
    
    retriever = Retriever()
    
    # ── 快速模式 ──
    print("⚡ 快速模式 (无MQE):")
    t0 = time.time()
    recall, mrr = evaluate(retriever, samples, k=Config.RERANK_TOP_K, enable_mqe=False)
    t1 = time.time()
    print(f"\n  Recall@{Config.RERANK_TOP_K}: {recall:.1%}  MRR: {mrr:.3f}  ({t1-t0:.0f}s)\n")
    
    # ── 精度模式 (MQE) ──
    print("🎯 精度模式 (MQE):")
    t0 = time.time()
    recall, mrr = evaluate(retriever, samples, k=Config.RERANK_TOP_K, enable_mqe=True)
    t1 = time.time()
    print(f"\n  Recall@{Config.RERANK_TOP_K}: {recall:.1%}  MRR: {mrr:.3f}  ({t1-t0:.0f}s)\n")
    
    # ── 精度模式 (MQE + 大候选池) ──
    print("🎯 精度模式 (MQE + 大池):")
    t0 = time.time()
    recall, mrr = evaluate(retriever, samples, k=Config.TOP_K, enable_mqe=True)
    t1 = time.time()
    print(f"\n  Recall@{Config.TOP_K}: {recall:.1%}  MRR: {mrr:.3f}  ({t1-t0:.0f}s)\n")

    # ── 精度模式 (HyDE only) ──
    print("🧪 HyDE only (无MQE):")
    t0 = time.time()
    recall, mrr = evaluate(retriever, samples, k=Config.RERANK_TOP_K, enable_mqe=False, enable_hyde=True)
    t1 = time.time()
    print(f"\n  Recall@5: {recall:.1%}  MRR: {mrr:.3f}  ({t1-t0:.0f}s)")


if __name__ == "__main__":
    main()
