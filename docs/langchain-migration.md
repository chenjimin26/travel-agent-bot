# LangChain 重构改动文档

## 概述

将项目从原生 OpenAI/chromadb 迁移到 LangChain 生态，嵌入层和 LLM 层实现 LangChain 接口，向量库使用 `langchain_chroma` 封装。

## 依赖变更

**requirements.txt**
- 删除: `sentence-transformers>=2.0.0`
- 新增: `langchain>=0.3.0`, `langchain-openai>=0.2.0`, `langchain-chroma>=0.2.0`, `langchain-core>=0.3.0`

## 文件改动明细

### app/rag/embeddings.py — 重写

**旧**: `EmbeddingClient` 类，直接调用 `openai.OpenAI.embeddings.create()`
**新**: `TongyiEmbeddings(Embeddings)` 类，实现 LangChain `Embeddings` 接口：
- `embed_documents(texts)` → 批量向量
- `embed_query(text)` → 单条向量
- 底层仍用 Tongyi DashScope API（`text-embedding-v3`）

### app/llm/qwen_client.py — 重写

**旧**: `QwenClient` 类，`chat()` / `chat_stream()` / `chat_with_context()`
**新**: `QwenLLM` 类，`invoke(messages) -> str`
- 兼容 `langchain_core` 调用约定
- 底层仍用 Tongyi DashScope API（`qwen3.5-plus`）

### app/rag/vector_store.py — 重写

**旧**: `chromadb.PersistentClient` + `self.collection.query()`
**新**: `langchain_chroma.Chroma`
- `add_texts(texts, metadatas, ids)` — 代替 `add()`
- `similarity_search(query, k)` — 代替 `search()`
- `similarity_search_with_score(query, k)` — 代替 `search_by_embedding()`
- `add_documents(docs, ids)` — 直接接受 LangChain `Document` 列表
- `as_retriever(search_kwargs)` — 返回 LangChain `Retriever`

### app/rag/retriever.py — 重写

**旧**: 直接调 `self.store.search_by_embedding()`
**新**: 调 `self.store.similarity_search_with_score()`
- `search_expanded()` 返回 `List[Document]`
- MQE/HyDE 逻辑不变，LLM 调用改为 `llm.invoke(messages) -> str`
- LuangChain `ChatPromptTemplate`（Tongyi 不兼容）

### app/rag/reranker.py — 重写

**旧**: `CrossEncoder` 本地模型 + `QwenClient` API 调用混合
**新**: 纯 LLM 批量打分
- 接受 `List[Document]` 或 `List[dict]`
- 返回 `List[Document]`
- LuangChain `ChatPromptTemplate`（Tongyi 不兼容）

### app/rag/chunker.py — 更新

**旧**: 返回 `List[Dict]`（`{"id", "content", "metadata"}`）
**新**: 返回 `List[Document]`（`langchain_core.documents.Document`）
- `page_content` = 景点格式化文本
- `metadata` = 城市/名称/标签/门票/开放时间/季节

### app/rag/indexer.py — 适配

**旧**: `store.add(documents, embeddings, metadatas, ids)`
**新**: `store.add_texts(texts, metadatas, ids)` — Chroma 自动调用 embedder

### app/api/chat.py — 重写

**旧**: `QwenClient.chat()` + `ChatResponse`
**新**: `llm.invoke(messages)` + 直接构造 `messages` 列表
- LuangChain `ChatPromptTemplate`（Tongyi 不兼容）
- 检索/重排序/生成链路不变

## 未改动的文件

| 文件 | 原因 |
|------|------|
| `app/config.py` | 配置独立，不需要 LangChain |
| `app/data/data_loader.py` | 纯数据加载 |
| `app/memory/memory.py` | 简单内存存储 |
| `app/models/schemas.py` | Pydantic 模型 |
| `app/api/health.py` | 健康检查端点 |
| `app/server.py` | FastAPI 入口 |
| `main.py` | CLI 入口 |

## 已知兼容性问题

- `langchain_openai.ChatOpenAI` 的 `invoke()` 在 Tongyi DashScope API 下会挂死，故未使用
- `langchain_openai.OpenAIEmbeddings` 返回 `InvalidParameter`，故用自定义 `TongyiEmbeddings`
- 两处均改用原生 `openai.OpenAI` 客户端包装 LangChain 接口

## 端到端验证

```
### 同里古镇
- 推荐理由：苏州著名的古镇，有东方小威尼斯之称。
- 门票：100 元
- 开放时间：08:00-18:00

### 甪直古镇
- 推荐理由：苏州著名的古镇，有神州水乡第一镇之称。
- 门票：78 元
- 开放时间：08:00-18:00

### 周庄古镇
- 推荐理由：中国六大古镇之一，有中国第一水乡之称。
- 门票：100 元
- 开放时间：08:00-18:00
```

✅ MQE 扩展检索 + LLM 重排序 + 格式化生成，链路完整。
