"""
Planner Agent — 行程规划与预算计算

根据检索到的景点，按天数编排行程，
计算总门票费用，确保不超预算。
"""
from app.llm.qwen_client import get_llm


PLANNER_PROMPT = """你是旅行行程精修师。已有初版攻略骨架和景点详细信息，请调整完善。

输出 JSON：
{
  "itinerary": [{"day": 1, "attractions": ["景点名"], "note": "说明", "theme": "主题"}],
  "total_ticket": 总门票费(元),
  "tips": ["建议"]
}

调整规则：
- 优先保留初版骨架的景点和主题，除非该景点KB搜不到
- KB有的景点优先使用KB的门票和开放时间
- 酒店位置尽可能靠近当天最后一个景点
- 每天2-3个景点"""

PLANNER_PROMPT_BUDGET = """你是旅行行程规划师。预算有限，优先免费或低价景点。

输出 JSON：同上格式。

要求：每天2-3个景点，优先门票免费或低于50元的。"""


class PlannerAgent:
    def __init__(self):
        self.llm = get_llm("kimi")

    def plan(self, attractions: list[dict], days: int, budget: float = 0,
             feedback: str = "", budget_mode: bool = False,
             guide_skeleton: dict = None, hotel_info: str = "") -> dict:
        import json

        # KB景点详情
        summary = ""
        for i, a in enumerate(attractions, 1):
            summary += f"[{i}] {a['name']} | 门票:{a.get('ticket','?')} | 时间:{a.get('open_time','?')} | 标签:{','.join(a.get('tags',[]))}\n"

        # Guide初版骨架
        skeleton_text = ""
        if guide_skeleton:
            skeleton_text = f"\n初版攻略骨架（优先参考）：\n{json.dumps(guide_skeleton, ensure_ascii=False, indent=2)}"

        prompt = PLANNER_PROMPT_BUDGET if budget_mode else PLANNER_PROMPT
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"天数：{days}天 | 预算：{budget}元\n\nKB景点详情：\n{summary}{skeleton_text}\n酒店信息：{hotel_info}\n{feedback}\n请调整完善行程，输出JSON。"}
        ]
        response = self.llm.invoke(messages)

        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            data = json.loads(response[start:end]) if start != -1 else {}
        except:
            data = {}

        return data
