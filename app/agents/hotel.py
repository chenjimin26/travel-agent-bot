"""
Hotel Agent — 酒店查询（美团旅行 CLI）

通过 mttravel CLI 查询真实酒店数据，
支持按城市、预算、位置、星级等条件筛选。
"""
import subprocess
from app.llm.qwen_client import get_llm
from app.config import Config


def _call_meituan(city: str, query: str) -> str:
    """调用美团旅行 CLI，返回酒店查询结果"""
    proc = subprocess.Popen(
        ["mttravel", city, query],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    try:
        stdout, _ = proc.communicate(timeout=120)
        return stdout.strip()
    except subprocess.TimeoutExpired:
        proc.kill()
        return "查询超时，请稍后重试"
    finally:
        proc.terminate()


HOTEL_PROMPT = """你是酒店推荐助手。根据美团返回的真实酒店数据，提取关键信息并格式化。

输出 JSON：
{
  "hotels": [
    {"name": "...", "price": "...", "rating": "...", "distance": "...", "highlights": "..."}
  ],
  "summary": "一句话总结推荐理由",
  "best_pick": {"name": "...", "reason": "..."}
}"""


class HotelAgent:
    def __init__(self):
        self.llm = get_llm("qwen-flash")

    def search(self, destination: str, attractions: list[str] = None, preferences: str = "") -> dict:
        """按景点就近查酒店"""
        import json

        # 优先按景点搜酒店，没景点则按城市搜
        if attractions and len(attractions) > 0:
            main_spot = attractions[0]
            query = f"{main_spot}附近1公里内的酒店"
        else:
            query = preferences or "推荐3家性价比高的酒店"

        raw = _call_meituan(destination, query)

        if not raw or "查询超时" in raw or "鉴权失败" in raw:
            return {"hotels": [], "summary": raw or "查询失败", "best_pick": None}

        # LLM 提取结构化信息
        messages = [
            {"role": "system", "content": HOTEL_PROMPT},
            {"role": "user", "content": f"目的地：{destination}\n偏好：{preferences}\n\n美团返回数据：\n{raw[:3000]}\n\n请提取关键信息，输出JSON。"}
        ]
        response = self.llm.invoke(messages)

        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            return json.loads(response[start:end]) if start != -1 else {}
        except:
            return {"hotels": [], "summary": "解析失败", "best_pick": None}
