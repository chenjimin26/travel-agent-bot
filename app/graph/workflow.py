"""
LangGraph Workflow — 多智能体编排

Supervisor → Retriever → Planner → Evaluator ⇄ Planner → Writer
                                            ↑ 审核不通过则重试(最多3次)
"""
from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.agents.supervisor import Supervisor
from app.agents.retriever import RetrieverAgent
from app.agents.planner import PlannerAgent
from app.agents.evaluator import EvaluatorAgent
from app.agents.writer import WriterAgent
from app.agents.transport import TransportAgent
from app.agents.hotel import HotelAgent
from app.agents.guide import GuideAgent

MAX_RETRIES = 3

# ── 节点函数 ──

def supervisor_node(state: AgentState) -> dict:
    agent = Supervisor()
    intent = agent.parse(state["query"])

    # 合并上一轮 intent：新 query 补充缺失字段
    prev = state.get("previous_intent") or {}
    for key in ["destination", "departure", "start_date", "days", "num_people", "budget"]:
        new_val = getattr(intent, key, None)
        prev_val = prev.get(key)
        is_empty = not new_val or new_val == "" or new_val == 0
        if is_empty and prev_val:
            setattr(intent, key, prev_val)

    if not intent.is_valid:
        missing = "、".join(intent.missing_fields)
        return {
            "intent": intent.model_dump(),
            "previous_intent": intent.model_dump(),
            "error": f"请提供以下信息：{missing}",
            "final_output": f"请补充以下信息后重新提问：**{missing}**"
        }

    return {
        "intent": intent.model_dump(),
        "previous_intent": intent.model_dump()
    }


def transport_node(state: AgentState) -> dict:
    intent = state["intent"]
    departure = intent.get("departure", "")
    destination = intent.get("destination", "")
    start_date = intent.get("start_date", "")
    days = intent.get("days", 3)

    if departure and destination:
        agent = TransportAgent()
        transport = agent.query(departure, destination, start_date, days)
        return {"transport": transport}

    return {"transport": {}}


def guide_node(state: AgentState) -> dict:
    intent = state["intent"]
    destination = intent.get("destination", "")
    days = intent.get("days", 1)
    prefs = intent.get("preferences", [])

    if destination:
        agent = GuideAgent()
        guide = agent.search(destination, days, prefs)
        return {"guide": guide}

    return {"guide": {}}


def retriever_node(state: AgentState) -> dict:
    agent = RetrieverAgent()
    intent = state["intent"]
    guide = state.get("guide", {})

    # 优先用攻略中的景点名搜索
    attraction_names = guide.get("attractions", [])
    query = " ".join(attraction_names[:3]) if attraction_names else intent.get("destination", "")

    attractions = agent.search(
        destination=intent.get("destination", ""),
        preferences=intent.get("preferences", [])
    )

    # 如果攻略中有景点名但 KB 搜不到，补一个全文搜索
    if attraction_names and len(attractions) < 3:
        for name in attraction_names:
            extras = agent.search(destination=name.split(" ")[0], preferences=[])
            for e in extras:
                if e not in attractions:
                    attractions.append(e)

    return {"attractions": attractions}


def hotel_node(state: AgentState) -> dict:
    intent = state["intent"]
    destination = intent.get("destination", "")
    guide = state.get("guide", {})

    if destination:
        agent = HotelAgent()
        attractions = guide.get("attractions", [])
        hotels = agent.search(destination, attractions)
        return {"hotels": hotels}

    return {"hotels": {}}


def planner_node(state: AgentState) -> dict:
    agent = PlannerAgent()
    intent = state["intent"]
    feedback = state["evaluation"].get("suggestions", []) if state.get("evaluation") else []

    plan = agent.plan(
        attractions=state["attractions"],
        days=intent.get("days", 1),
        budget=intent.get("budget", 0)
    )

    if feedback and state.get("retry_count", 0) > 0:
        plan["_feedback"] = feedback

    return {"plan": plan}


def evaluator_node(state: AgentState) -> dict:
    agent = EvaluatorAgent()
    intent = state["intent"]
    evaluation = agent.evaluate(
        plan=state["plan"],
        budget=intent.get("budget", 0)
    )
    return {
        "evaluation": evaluation,
        "retry_count": state.get("retry_count", 0) + 1
    }


def writer_node(state: AgentState) -> dict:
    agent = WriterAgent()
    output = agent.write(
        plan=state["plan"],
        attractions=state["attractions"],
        intent=state["intent"],
        transport=state.get("transport"),
        hotels=state.get("hotels")
    )
    return {"final_output": output}


# ── 路由函数 ──

def route_after_supervisor(state: AgentState) -> str:
    if state.get("error"):
        return "end"
    return "transport"

def route_after_eval(state: AgentState) -> str:
    evaluation = state.get("evaluation", {})
    retry_count = state.get("retry_count", 0)

    if evaluation.get("passed"):
        return "writer"

    if retry_count < MAX_RETRIES:
        return "planner"

    return "writer"   # 超过重试次数，强制输出


# ── 构建图 ──

def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("transport", transport_node)
    builder.add_node("guide", guide_node)
    builder.add_node("retriever", retriever_node)
    builder.add_node("hotel", hotel_node)
    builder.add_node("planner", planner_node)
    builder.add_node("evaluator", evaluator_node)
    builder.add_node("writer", writer_node)

    builder.set_entry_point("supervisor")
    builder.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {"transport": "transport", "end": END}
    )
    builder.add_edge("transport", "guide")
    builder.add_edge("guide", "retriever")
    builder.add_edge("retriever", "hotel")
    builder.add_edge("hotel", "planner")
    builder.add_edge("planner", "evaluator")

    builder.add_conditional_edges(
        "evaluator",
        route_after_eval,
        {"planner": "planner", "writer": "writer"}
    )

    builder.add_edge("writer", END)

    return builder.compile()


travel_graph = build_graph()
