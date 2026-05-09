import pytest
from app.data.data_loader import load_city
from app.rag.chunker import chunk_one_city
from app.rag.vector_store import VectorStore
from app.rag.retriever import Retriever
from app.rag.reranker import Reranker


class TestIntegration:
    def test_full_flow(self):
        print("1. 测试数据加载...")
        attractions = load_city("beijing", "./data/attractions")
        assert len(attractions) > 0, "应该加载到景点数据"
        print(f"  ✓ 加载了 {len(attractions)} 个景点")
        
        print("2. 测试 chunk...")
        chunks = chunk_one_city("beijing", "./data/attractions")
        assert len(chunks) > 0, "应该生成 chunks"
        assert "content" in chunks[0], "chunk 应该有 content"
        assert "metadata" in chunks[0], "chunk 应该有 metadata"
        print(f"  ✓ 生成了 {len(chunks)} 个 chunks")
        
        print("3. 测试召回...")
        retriever = Retriever()
        results = retriever.search("北京故宫", top_k=3)
        assert results is not None, "应该返回结果"
        assert len(results.get("documents", [[]])[0]) > 0, "应该召回文档"
        print(f"  ✓ 召回成功")
        
        print("4. 测试重排...")
        reranker = Reranker()
        reranked = reranker.rerank_cross("北京故宫", results, top_k=2)
        assert len(reranked) > 0, "重排后应该有结果"
        print(f"  ✓ 重排成功")
        
        print("\n✅ 全流程测试通过！")


if __name__ == "__main__":
    test = TestIntegration()
    test.test_full_flow()