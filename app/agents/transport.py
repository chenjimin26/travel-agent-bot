"""
Transport Agent — 出行交通查询（美团旅行 CLI）
"""
import json
from datetime import date, timedelta
from app.llm.qwen_client import get_llm
from app.tools.meituan import call_meituan


TRANSPORT_PROMPT_NORMAL = """你是出行交通助手。从车次中选最佳往返。优先高铁二等座。
如果当天没有合适的车次，可以选次日或隔日车次。
输出 JSON：{"go_train":{"train_no","depart","arrive","price","seat","date"},"back_train":{...},"total_transport_cost":N,"suggestion":"..."}"""

TRANSPORT_PROMPT_BUDGET = """你是出行交通助手。预算有限，优先选最便宜的车次（硬座/动车），其次才考虑高铁。
如果当天没有合适的车次，可以选次日或隔日车次。
输出 JSON：{"go_train":{"train_no","depart","arrive","price","seat","date"},"back_train":{...},"total_transport_cost":N,"suggestion":"..."}"""


class TransportAgent:
    def __init__(self):
        self.llm = get_llm("qwen-flash")
    def query(self, departure: str, destination: str, start_date: str = None,
              days: int = 3, budget_mode: bool = False,
              departure_time: str = "", return_by: str = "") -> dict:
        # 查去程（预算模式优先硬座/动车）
        date_hint = f"{start_date}出发" if start_date else ""
        go_query = f"到{destination}的火车票{date_hint}"
        if budget_mode:
            go_query = f"到{destination}最便宜的火车票{date_hint}"
        go_raw = call_meituan(departure, go_query)

        # 返程日期
        from datetime import date, timedelta
        if start_date:
            try:
                back_date = (date.fromisoformat(start_date) + timedelta(days=days)).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                back_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
            back_date_hint = f"{back_date}出发"
        else:
            back_date_hint = ""

        # 查返程
        back_raw = call_meituan(destination, f"到{departure}的火车票{back_date_hint}")

        if "查询超时" in go_raw or not go_raw:
            return {"go_train": None, "back_train": None, "total_transport_cost": 0, "suggestion": "车票查询超时"}

        prompt = TRANSPORT_PROMPT_BUDGET if budget_mode else TRANSPORT_PROMPT_NORMAL
        # 有时间约束时，改 prompt
        if departure_time or return_by:
            prompt = """你是出行交通助手。从车次中选最佳往返。
如果当天没有合适的车次，必须选次日或隔日车次，在 date 字段标注实际出发日期。
输出 JSON：{"go_train":{"train_no","depart","arrive","price","seat","date"},"back_train":{...},"total_transport_cost":N,"suggestion":"..."}"""
        
        time_constraint = ""
        if departure_time:
            time_constraint = f"""

=== 时间硬约束（必须遵守，否则结果无效）===
去程出发时间 ≥ {departure_time}。当天无匹配必须选次日最早符合条件的车次，在 date 字段标注实际出发日期。"""
        
        return_constraint = ""
        if return_by:
            return_constraint = f"""

=== 返程时间硬约束 ===
返程只能选到达时间 ≤ {return_by} 的车次。
到达时间晚于 {return_by} 的车次全部无效，禁止选择。"""
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"去程({departure}→{destination})：\n{go_raw[:3000]}\n\n返程({destination}→{departure})：\n{back_raw[:2000]}\n{time_constraint}{return_constraint}\n选最佳往返车次，输出JSON。"}
        ]
        response = self.llm.invoke(messages)

        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            return json.loads(response[start:end]) if start != -1 else {}
        except:
            return {}
