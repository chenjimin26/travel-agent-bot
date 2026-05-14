"""
LangGraph State — 贯穿全流程的数据结构
"""
from typing import TypedDict, Annotated
import operator


class AgentState(TypedDict):
    # ── 输入 ──
    query: str
    mode: str                         # "fast" | "precision"

    # ── Supervisor 输出 ──
    intent: dict
    previous_intent: dict              # 上一轮解析结果，用于合并补全

    # ── Transport 输出 ──
    transport: dict                   # {go_train, back_train, total_transport_cost, suggestion}

    # ── Hotel 输出 ──
    hotels: dict

    # ── Guide 输出 ──
    guide: dict                       # {title, attractions: [...], daily_plan: [...], tips: [...]}

    # ── Retriever 输出 ──
    attractions: Annotated[list, operator.add]   # 景点列表

    # ── Planner 输出 ──
    plan: dict                        # {itinerary: [...], total_ticket: N, tips: [...]}

    # ── Evaluator 输出 ──
    evaluation: dict                  # {passed: bool, issues: [...], suggestions: [...]}
    retry_count: int                  # 重试次数

    # ── Writer 输出 ──
    final_output: str                 # 最终攻略

    # ── 错误 ──
    error: str
    transport_retries: int
    guide_retries: int
    retriever_retries: int
    hotel_retries: int
    budget_mode: int               # 0=正常 1=预算超标切便宜模式
