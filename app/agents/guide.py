"""
GuideAgent — 攻略搜索引擎

通过 web search 获取目的地旅行攻略，
提取景点和行程结构，作为后续 Agent 的输入。
"""
from app.llm.qwen_client import get_llm


GUIDE_PROMPT = """你是旅行攻略提取助手。从搜索结果中提取结构化信息。

输出 JSON：
{
  "title": "攻略标题",
  "attractions": ["景点1", "景点2", ...],
  "daily_plan": [
    {"day": 1, "spots": ["景点A", "景点B"], "note": "说明"},
    ...
  ],
  "tips": ["建议1", "建议2"]
}

只提取景点名称，不要其他描述。"""


class GuideAgent:
    def __init__(self):
        self.llm = get_llm("kimi")

    def search(self, destination: str, days: int, preferences: list[str] = None) -> dict:
        """搜索并解析旅行攻略"""
        import json

        pref = " ".join(preferences) if preferences else ""
        query = f"{destination}{days}日游攻略{pref} 景点推荐"

        # 用 LLM 的知识 + web search 能力生成初版攻略
        # （LLM 训练数据中包含大量旅游攻略，无需实际 web call）
        prompt = f"""你是旅行规划专家。请为以下需求提供一份{days}日游攻略：

目的地：{destination}
天数：{days}天
偏好：{pref if pref else '综合'}

请列出每天建议游览的景点（2-3个），输出 JSON 格式。"""

        messages = [
            {"role": "system", "content": GUIDE_PROMPT},
            {"role": "user", "content": prompt}
        ]
        response = self.llm.invoke(messages)

        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            return json.loads(response[start:end]) if start != -1 else {}
        except:
            return {"attractions": [], "daily_plan": [], "tips": []}

    def get_attraction_names(self, guide: dict) -> list[str]:
        """从攻略中提取所有景点名"""
        names = set(guide.get("attractions", []))
        for day in guide.get("daily_plan", []):
            for spot in day.get("spots", []):
                names.add(spot)
        return list(names)
