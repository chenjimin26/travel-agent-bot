"""
LangGraph Workflow — 多智能体编排
Supervisor → fanout → {Transport|Guide|Retriever} → Hotel → Planner → Evaluator → Writer
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


# ═══════════════════════════════════════════════
# 节点函数
# ═══════════════════════════════════════════════

def supervisor_node(state: AgentState) -> dict:
    agent = Supervisor()
    intent = agent.parse(state["query"])
    prev = state.get("previous_intent") or {}
    for key in ["destination", "departure", "start_date", "days", "num_people", "budget"]:
        new_val = getattr(intent, key, None)
        prev_val = prev.get(key)
        if (not new_val or new_val == "" or new_val == 0) and prev_val:
            setattr(intent, key, prev_val)
    if not intent.is_valid:
        missing = "、".join(intent.missing_fields)
        return {"intent": intent.model_dump(), "previous_intent": intent.model_dump(),
                "error": f"请提供以下信息：{missing}",
                "final_output": f"请补充以下信息后重新提问：**{missing}**"}
    return {"intent": intent.model_dump(), "previous_intent": intent.model_dump()}


def transport_node(state: AgentState) -> dict:
    intent = state["intent"]
    departure = intent.get("departure", "")
    destination = intent.get("destination", "")
    start_date = intent.get("start_date", "")
    days = intent.get("days", 3)
    retries = state.get("transport_retries", 0)
    budget_mode = state.get("budget_mode", 0)

    if departure and destination:
        agent = TransportAgent()
        transport = agent.query(departure, destination, start_date, days,
                                budget_mode=budget_mode,
                                departure_time=intent.get("departure_time", ""),
                                return_by=intent.get("return_by", ""))
        if not transport.get("go_train", {}).get("train_no"):
            retries += 1
        elif "未匹配" in str(transport["go_train"]["train_no"]) or "无符合" in str(transport["go_train"]["train_no"]):
            retries += 1
        else:
            retries = retries  # 有数据，保持计数
            if retries >= 3:
                return {"transport": transport, "transport_retries": retries,
                        "error": f"交通查询失败(已重试{retries}次)"}
        return {"transport": transport, "transport_retries": retries}
    return {"transport": {}}


def guide_node(state: AgentState) -> dict:
    intent = state["intent"]
    destination = intent.get("destination", "")
    days = intent.get("days", 1)
    prefs = intent.get("preferences", [])
    start_date = intent.get("start_date", "")
    retries = state.get("guide_retries", 0)

    if destination:
        agent = GuideAgent()
        guide = agent.search(destination, days, prefs, start_date)
        if not guide.get("attractions"):
            retries += 1
            if retries >= 3:
                return {"guide": guide, "guide_retries": retries,
                        "error": f"攻略生成失败(已重试{retries}次)"}
        return {"guide": guide, "guide_retries": retries}
    return {"guide": {}}


def retriever_node(state: AgentState) -> dict:
    agent = RetrieverAgent()
    intent = state["intent"]
    guide = state.get("guide", {})
    retries = state.get("retriever_retries", 0)
    attraction_names = guide.get("attractions", [])

    attractions = agent.search(
        destination=intent.get("destination", ""),
        preferences=intent.get("preferences", [])
    )
    if attraction_names and len(attractions) < 3:
        for name in attraction_names:
            extras = agent.search(destination=name.split(" ")[0], preferences=[])
            for e in extras:
                if e not in attractions:
                    attractions.append(e)

    if not attractions:
        retries += 1
        if retries >= 3:
            return {"attractions": attractions, "retriever_retries": retries,
                    "error": f"景点检索失败(已重试{retries}次)"}
    return {"attractions": attractions, "retriever_retries": retries}


def hotel_node(state: AgentState) -> dict:
    intent = state["intent"]
    destination = intent.get("destination", "")
    guide = state.get("guide", {})
    budget_mode = state.get("budget_mode", 0)
    retries = state.get("hotel_retries", 0)

    if destination:
        agent = HotelAgent()
        attractions = guide.get("attractions", [])
        hotels = agent.search(destination, attractions, budget_mode=budget_mode)
        if not hotels.get("hotels"):
            retries += 1
            if retries >= 3:
                return {"hotels": hotels, "hotel_retries": retries,
                        "error": f"酒店查询失败(已重试{retries}次)"}
        return {"hotels": hotels, "hotel_retries": retries}
    return {"hotels": {}}


def planner_node(state: AgentState) -> dict:
    agent = PlannerAgent()
    intent = state["intent"]
    retry = state.get("retry_count", 0)
    feedback = ""
    if retry > 0:
        eval_result = state.get("evaluation", {})
        issues = eval_result.get("issues", [])
        suggestions = eval_result.get("suggestions", [])
        if issues or suggestions:
            feedback = "⚠️ 上一版审核不通过：\n"
            feedback += "\n".join([f"- {i}" for i in issues])
            feedback += "\n" + "\n".join([f"- {s}" for s in suggestions])

    budget_mode = state.get("budget_mode", 0)
    plan = agent.plan(
        attractions=state["attractions"],
        days=intent.get("days", 1),
        budget=intent.get("budget", 0),
        feedback=feedback,
        budget_mode=budget_mode,
        guide_skeleton=state.get("guide", {}).get("daily_plan"),
        hotel_info=state.get("hotels", {}).get("summary", "")
    )
    return {"plan": plan}


def evaluator_node(state: AgentState) -> dict:
    agent = EvaluatorAgent()
    intent = state["intent"]
    evaluation = agent.evaluate(
        plan=state["plan"],
        budget=intent.get("budget", 0),
        transport=state.get("transport"),
        hotels=state.get("hotels"),
        num_people=intent.get("num_people") or 1,
        days=intent.get("days", 1)
    )
    is_over_budget = any("预算超标" in i for i in evaluation.get("issues", []))
    prev_budget_mode = state.get("budget_mode", 0)
    budget_mode = 1 if (is_over_budget and prev_budget_mode == 0) else prev_budget_mode
    return {"evaluation": evaluation, "retry_count": state.get("retry_count", 0) + 1, "budget_mode": budget_mode}


def writer_node(state: AgentState) -> dict:
    error = state.get("error", "")
    if error:
        return {"final_output": f"❌ 规划失败：{error}\n\n请调整查询条件后重试。"}
    agent = WriterAgent()
    output = agent.write(
        plan=state["plan"], attractions=state["attractions"], intent=state["intent"],
        transport=state.get("transport"), hotels=state.get("hotels"), guide=state.get("guide", {})
    )
    return {"final_output": output}


# ═══════════════════════════════════════════════
# 路由函数
# ═══════════════════════════════════════════════

def route_after_supervisor(state: AgentState) -> str:
    return "end" if state.get("error") else "fanout"


def fanout_node(state: AgentState) -> dict:
    return {}


def route_after_transport(state: AgentState) -> str:
    if state.get("error"):
        return "writer"
    go = state.get("transport", {}).get("go_train") or {}
    train_no = str(go.get("train_no", ""))
    is_empty = not train_no or "未匹配" in train_no or "无符合" in train_no
    if is_empty and state.get("transport_retries", 0) < 3:
        return "transport"
    if state.get("transport_retries", 0) >= 3:
        return "writer"
    return "hotel"

def route_after_guide(state: AgentState) -> str:
    if state.get("error"):
        return "writer"
    if not state.get("guide", {}).get("attractions") and state.get("guide_retries", 0) < 3:
        return "guide"
    if state.get("guide_retries", 0) >= 3:
        return "writer"
    return "hotel"

def route_after_retriever(state: AgentState) -> str:
    if state.get("error"):
        return "writer"
    if not state.get("attractions") and state.get("retriever_retries", 0) < 3:
        return "retriever"
    if state.get("retriever_retries", 0) >= 3:
        return "writer"
    return "hotel"


def route_after_hotel(state: AgentState) -> str:
    if state.get("error"):
        return "writer"
    if not state.get("hotels", {}).get("hotels") and state.get("hotel_retries", 0) < 3:
        return "hotel"
    if state.get("hotel_retries", 0) >= 3:
        return "writer"
    return "planner"


def route_after_eval(state: AgentState) -> str:
    if state.get("error"):
        return "writer"
    if state.get("evaluation", {}).get("passed"):
        return "writer"
    if state.get("budget_mode") == 1 and state.get("retry_count", 0) <= MAX_RETRIES:
        return "fanout"
    return "writer"


# ═══════════════════════════════════════════════
# 构建图
# ═══════════════════════════════════════════════

def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("fanout", fanout_node)
    builder.add_node("transport", transport_node)
    builder.add_node("guide", guide_node)
    builder.add_node("retriever", retriever_node)
    builder.add_node("hotel", hotel_node)
    builder.add_node("planner", planner_node)
    builder.add_node("evaluator", evaluator_node)
    builder.add_node("writer", writer_node)

    builder.set_entry_point("supervisor")
    builder.add_conditional_edges("supervisor", route_after_supervisor, {"fanout": "fanout", "end": END})

    # 并行分发
    builder.add_edge("fanout", "transport")
    builder.add_edge("fanout", "guide")
    builder.add_edge("fanout", "retriever")

    # 各节点自检后汇合
    builder.add_conditional_edges("transport", route_after_transport, {"transport": "transport", "hotel": "hotel", "writer": "writer"})
    builder.add_conditional_edges("guide", route_after_guide, {"guide": "guide", "hotel": "hotel", "writer": "writer"})
    builder.add_conditional_edges("retriever", route_after_retriever, {"retriever": "retriever", "hotel": "hotel", "writer": "writer"})

    builder.add_conditional_edges("hotel", route_after_hotel, {"hotel": "hotel", "planner": "planner", "writer": "writer"})
    builder.add_edge("planner", "evaluator")

    builder.add_conditional_edges("evaluator", route_after_eval,
        {"fanout": "fanout", "writer": "writer"})

    builder.add_edge("writer", END)
    return builder.compile()


travel_graph = build_graph()
