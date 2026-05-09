"""
Writer Agent — 完整攻略输出

整合景点、酒店、交通信息，输出完整行程攻略，
包含总预算计算。
"""
from app.llm.qwen_client import get_llm


WRITER_PROMPT = """你是旅行攻略文案师。输出一份完整的旅行攻略，必须包含：

1. 🚄 交通：往返车次、时间、费用
2. 🏨 住宿：推荐酒店、价格
3. 🎫 行程：每天安排，景点名称、门票、推荐理由
4. 💰 预算汇总表格：交通费 + 住宿费 + 门票费 = 总费用"""


class WriterAgent:
    def __init__(self):
        self.llm = get_llm("qwen-flash")

    def write(self, plan: dict, attractions: list[dict], intent: dict,
              transport: dict = None, hotels: dict = None) -> str:
        import json

        parts = []

        if transport and transport.get("go_train"):
            g = transport["go_train"]
            b = transport["back_train"]
            parts.append(f"🚄 交通：去程 {g.get('train_no','?')} {g.get('depart','?')}-{g.get('arrive','?')} ￥{g.get('price',0)} | 返程 {b.get('train_no','?')} ￥{b.get('price',0)} | 合计 ￥{transport.get('total_transport_cost',0)}")

        if hotels and hotels.get("hotels"):
            hl = "\n".join([f"- {h.get('name','?')} {h.get('price','?')}" for h in hotels["hotels"][:3]])
            parts.append(f"🏨 酒店：\n{hl}")

        attrs_text = "\n".join([f"- {a['name']} | 门票:{a.get('ticket','?')} | 时间:{a.get('open_time','?')}" for a in attractions[:5]])
        parts.append(f"🎫 景点：\n{attrs_text}")

        plan_text = json.dumps(plan, ensure_ascii=False, indent=2) if plan else "{}"

        user_content = f"""目的地：{intent.get('destination','')} | {intent.get('days',1)}天 | 预算：{intent.get('budget',0)}元

{chr(10).join(parts)}

行程计划：{plan_text}

请输出完整攻略，包含预算汇总表格。"""

        messages = [
            {"role": "system", "content": WRITER_PROMPT},
            {"role": "user", "content": user_content}
        ]
        return self.llm.invoke(messages)