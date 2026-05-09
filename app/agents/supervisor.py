"""
Supervisor Agent — 意图解析与参数校验

解析用户 query，提取必要参数。
目的地和天数为必填项，缺失则要求用户补充。
"""
from pydantic import BaseModel, Field
from app.llm.qwen_client import get_llm


class TravelIntent(BaseModel):
    destination: str | None = Field(default=None, description="目的地城市")
    departure: str | None = Field(default=None, description="出发地，必填")
    start_date: str | None = Field(default=None, description="出发日期 YYYY-MM-DD")
    days: int = Field(default=0, description="旅行天数，必填")
    budget: float = Field(default=0, description="总预算(元)，0表示无限制")
    preferences: list[str] = Field(default=[], description="偏好标签")
    num_people: int | None = Field(default=None, description="人数，必填")

    @property
    def missing_fields(self) -> list[str]:
        missing = []
        if not self.destination:
            missing.append("目的地")
        if not self.departure:
            missing.append("出发地")
        if not self.start_date:
            missing.append("出发日期(如5月15日)")
        if not self.days or self.days <= 0:
            missing.append("旅行天数")
        if not self.num_people:
            missing.append("人数")
        return missing

    @property
    def is_valid(self) -> bool:
        return len(self.missing_fields) == 0


SUPERVISOR_PROMPT = """你是旅行规划总指挥。从用户输入中提取信息。

必填字段（缺一不可，用户没提供就设为null）：
- destination: 目的地城市
- departure: 出发地城市
- start_date: 出发日期 YYYY-MM-DD
- days: 旅行天数
- num_people: 人数（没提就设null）

可选字段：
- budget: 总预算(元)（没提设0）
- preferences: 偏好列表

输出 JSON。"""


class Supervisor:
    def __init__(self):
        self.llm = get_llm("qwen-plus")

    def parse(self, query: str) -> TravelIntent:
        import json
        messages = [
            {"role": "system", "content": SUPERVISOR_PROMPT},
            {"role": "user", "content": f"用户输入：{query}\n\n输出JSON："}
        ]
        response = self.llm.invoke(messages)
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            data = json.loads(response[start:end]) if start != -1 else {}
        except:
            data = {}

        return TravelIntent(
            destination=data.get("destination") or None,
            departure=data.get("departure") or None,
            start_date=data.get("start_date") or None,
            days=int(data.get("days", 0) or 0),
            budget=float(data.get("budget", 0) or 0),
            preferences=data.get("preferences") or [],
            num_people=data.get("num_people") or None,
        )
