from fastapi import APIRouter, HTTPException
import json, os
from app.models.schemas import ChatRequest, ChatResponse
from app.rag.retriever import Retriever
from app.llm.qwen_client import llm
from app.memory.memory import Memory
from app.config import Config
from app.graph.workflow import travel_graph

router = APIRouter(prefix="/api/v1", tags=["chat"])

retriever = Retriever()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SESSION_DIR = os.path.join(BASE_DIR, "data", "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

sessions: dict[str, Memory] = {}


def _load_session(session_id: str) -> Memory | None:
    path = os.path.join(SESSION_DIR, f"{session_id}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        mem = Memory()
        mem.buffer = [(q, a) for q, a in data.get("buffer", [])]
        mem.summary = data.get("summary", "")
        mem.previous_intent = data.get("intent", {})
        return mem
    except:
        return None


def _save_session(session_id: str, mem: Memory):
    path = os.path.join(SESSION_DIR, f"{session_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "buffer": mem.buffer,
            "summary": mem.summary,
            "intent": mem.previous_intent
        }, f, ensure_ascii=False, indent=2)


def _get_memory(session_id: str | None) -> Memory:
    if not session_id:
        session_id = "__default__"
    if session_id not in sessions:
        mem = _load_session(session_id)
        sessions[session_id] = mem if mem else Memory()
    return sessions[session_id]


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    query = request.message
    mem = _get_memory(request.session_id)
    precision = request.mode == "precision"

    if precision:
        try:
            result = travel_graph.invoke({
                "query": query,
                "mode": request.mode,
                "attractions": [],
                "retry_count": 0,
                "error": "",
                "previous_intent": mem.previous_intent
            })
            response = result.get("final_output", "系统处理超时，请重试")
            sources = result.get("attractions", [])
            if result.get("intent"):
                mem.previous_intent = result["intent"]
        except Exception as e:
            response = f"系统异常：{str(e)[:100]}，请稍后重试"
            sources = []
    else:
        docs = retriever.search_expanded(
            query,
            k=Config.RERANK_TOP_K,
            enable_mqe=False,
            enable_hyde=False,
            pool_multiplier=Config.FAST_POOL_MULTIPLIER
        )

        context = "\n".join([f"- {doc.page_content}" for doc in docs])
        history = mem.get_context()

        user_content = f"""参考信息：
{context}

问题：{query}

请严格按格式回答，每个景区独立成段，门票价格不要换行。"""

        if history:
            user_content = history + "\n\n" + user_content

        messages = [
            {"role": "system", "content": Config.SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        response = llm.invoke(messages)

        sources = []
        for doc in docs:
            sources.append({
                "name": doc.metadata.get("name", ""),
                "city": doc.metadata.get("city", ""),
                "ticket": doc.metadata.get("ticket", ""),
                "open_time": doc.metadata.get("open_time", ""),
                "best_season": doc.metadata.get("best_season", ""),
                "tags": doc.metadata.get("tags", []),
                "description": doc.page_content[:200]
            })

    mem.add(query, response)
    _save_session(request.session_id or "__default__", mem)

    return ChatResponse(message=response, sources=sources)
