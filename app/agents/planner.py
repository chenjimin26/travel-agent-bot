"""
Planner Agent — 行程规划与预算计算

根据检索到的景点，按天数编排行程，
计算总门票费用，确保不超预算。
"""
from app.llm.qwen_client import get_llm


PLANNER_PROMPT = """你是旅行行程规划师。根据景点信息，编排每日行程。

输出 JSON：
{
  "itinerary": [
    {
      "day": 1,
      "attractions": ["景点名1", "景点名2"],
      "note": "当天安排说明"
    }
  ],
  "total_ticket": 总门票费用(元),
  "tips": ["旅行建议1", "旅行建议2"]
}

要求：
- 每天安排2-3个景点，不要太多
- 考虑地理位置合理性
- 门票按成人价计算"""


class PlannerAgent:
    def __init__(self):
        self.llm = get_llm("kimi")

    def plan(self, attractions: list[dict], days: int, budget: float = 0) -> dict:
        import json

        # 构建景点摘要
        summary = ""
        for i, a in enumerate(attractions, 1):
            summary += f"[{i}] {a['name']} | 门票:{a.get('ticket','?')} | 时间:{a.get('open_time','?')} | 标签:{','.join(a.get('tags',[]))}\n"

        messages = [
            {"role": "system", "content": PLANNER_PROMPT},
            {"role": "user", "content": f"旅行天数：{days}天\n预算：{budget}元（0表示不限）\n\n景点列表：\n{summary}\n\n请编排行程，输出JSON。"}
        ]
        response = self.llm.invoke(messages)

        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            data = json.loads(response[start:end]) if start != -1 else {}
        except:
            data = {}

        return data
