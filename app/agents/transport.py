"""
Transport Agent — 出行交通查询（美团旅行 CLI）

通过 mttravel CLI 查询真实火车票/机票数据。
"""
import json
import subprocess
from app.llm.qwen_client import get_llm


def _call_meituan(city: str, query: str) -> str:
    """调用美团旅行 CLI"""
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
        return "查询超时"
    finally:
        proc.terminate()


TRANSPORT_PROMPT = """你是出行交通助手。从火车票/机票数据中选择最合适的往返车次。
优先高铁二等座，去程早班、返程晚班。

输出 JSON：{"go_train":{"train_no","depart","arrive","price","seat"},"back_train":{...},"total_transport_cost":N,"suggestion":"..."}"""


class TransportAgent:
    def __init__(self):
        self.llm = get_llm("qwen-flash")

    def query(self, departure: str, destination: str, start_date: str = None, days: int = 3) -> dict:
        # 查去程
        date_hint = f"{start_date}出发" if start_date else ""
        go_raw = _call_meituan(departure, f"到{destination}的火车票{date_hint}")

        # 返程日期
        from datetime import date, timedelta
        if start_date:
            back_date = (date.fromisoformat(start_date) + timedelta(days=days)).strftime("%Y-%m-%d")
            back_date_hint = f"{back_date}出发"
        else:
            back_date_hint = ""

        # 查返程
        back_raw = _call_meituan(destination, f"到{departure}的火车票{back_date_hint}")

        if "查询超时" in go_raw or not go_raw:
            return {"go_train": None, "back_train": None, "total_transport_cost": 0, "suggestion": "车票查询超时"}

        messages = [
            {"role": "system", "content": TRANSPORT_PROMPT},
            {"role": "user", "content": f"去程({departure}→{destination})：\n{go_raw[:3000]}\n\n返程({destination}→{departure})：\n{back_raw[:2000]}\n\n选最佳往返车次，输出JSON。"}
        ]
        response = self.llm.invoke(messages)

        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            return json.loads(response[start:end]) if start != -1 else {}
        except:
            return {}
