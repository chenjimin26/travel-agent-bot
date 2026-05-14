"""
Supervisor Agent — 意图解析与参数校验

解析用户 query，提取必要参数。
目的地和天数为必填项，缺失则要求用户补充。
"""
from pydantic import BaseModel, Field


class TravelIntent(BaseModel):
    destination: str | None = Field(default=None, description="目的地城市")
    departure: str | None = Field(default=None, description="出发地，必填")
    start_date: str | None = Field(default=None, description="出发日期 YYYY-MM-DD")
    days: int = Field(default=0, description="旅行天数，必填")
    budget: float = Field(default=0, description="总预算(元)，0表示无限制")
    preferences: list[str] = Field(default=[], description="偏好标签")
    num_people: int | None = Field(default=None, description="人数，必填")
    departure_time: str = Field(default="", description="最早出发时间，如15:00、18:00")
    return_by: str = Field(default="", description="最晚到达时间，如08:00")

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


SUPERVISOR_PROMPT = """你是参数提取助手。今天是{today}，星期{weekday}。

任务：将用户自然语言转换为结构化旅行参数。

规则：
- "这周五""下周一""明天""后天"等 → 算成具体日期 YYYY-MM-DD
- "周末" → 默认周五出发，玩2天
- "三天两晚""3天2晚" → days=3
- 只提城市名没提出发地 → departure=null（后面会问）
- 预算没提 → budget=0
- "周一晚上8点以后"→departure_time="20:00", 无匹配时可放宽到次日凌晨
- "晚上出发"→departure_time="18:00", "下午三点以后"→"15:00", "中午以后"→"12:00"
- "周一早上八点之前回来"→return_by="08:00"
- 没提返回时间 → return_by=""
- 出站时间无匹配车次时放宽到次日/跨日

输出 JSON：
{{"destination":"苏州","departure":"盐城","start_date":"2026-05-15","days":3,"num_people":2,"budget":0,"preferences":[]}}"""


class Supervisor:
    def __init__(self):
        from langchain_openai import ChatOpenAI
        from app.config import Config
        self.llm = ChatOpenAI(
            model=Config.MODEL_REGISTRY.get("qwen-flash", Config.LLM_MODEL),
            openai_api_key=Config.DASHSCOPE_API_KEY,
            openai_api_base=Config.BASE_URL,
            temperature=0
        )

    def parse(self, query: str) -> TravelIntent:
        from datetime import date
        today = date.today()
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        prompt = SUPERVISOR_PROMPT.format(
            today=today.strftime("%Y-%m-%d"),
            weekday=weekdays[today.weekday()]
        )
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"用户输入：{query}"}
        ]
        response = self.llm.invoke(messages)
        result = response.content

        import json
        try:
            start = result.find("{")
            end = result.rfind("}") + 1
            data = json.loads(result[start:end]) if start != -1 else {}
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
            departure_time=data.get("departure_time", ""),
            return_by=data.get("return_by", ""),
        )
