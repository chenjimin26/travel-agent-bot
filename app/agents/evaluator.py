"""
Evaluator Agent — 硬计算 + LLM 软检查

硬检查：代码做预算加减法，不依赖 LLM
软检查：LLM 审核格式、时间冲突、景点合理性
"""
import json
from app.llm.qwen_client import get_llm

SOFT_CHECK_PROMPT = """你是旅行方案审核员。检查行程的软性问题：

1. 每天景点数是否合理（2-3个最佳，不超过4个）
2. 是否有时间冲突
3. 格式是否完整

输出 JSON：{"issues": [...], "suggestions": [...]}"""


class EvaluatorAgent:
    def __init__(self):
        self.llm = get_llm("deepseek")

    def evaluate(self, plan: dict, budget: float = 0,
                 transport: dict = None, hotels: dict = None,
                 num_people: int = 1, days: int = 1) -> dict:

        issues = []
        suggestions = []

        # ── 硬计算：预算检查 ──
        if budget > 0:
            # 1. 交通费（人数×往返）
            transport_cost = 0
            if transport and transport.get("total_transport_cost"):
                transport_cost = transport["total_transport_cost"] * num_people

            # 2. 酒店费（均价 × 天数）
            hotel_cost = 0
            if hotels and hotels.get("hotels"):
                prices = []
                for h in hotels["hotels"]:
                    p = h.get("price", "")
                    try:
                        prices.append(float(p.replace("￥", "").replace("起", "").replace("/晚", "").strip()))
                    except:
                        pass
                if prices:
                    hotel_cost = (sum(prices) / len(prices)) * (days - 1)

            # 3. 门票费
            ticket_cost = 0
            if plan and plan.get("total_ticket"):
                try:
                    ticket_cost = float(plan["total_ticket"])
                except:
                    pass

            total = transport_cost + hotel_cost + ticket_cost

            if total > budget:
                issues.append(
                    f"预算超标：交通{transport_cost:.0f} + 酒店{hotel_cost:.0f} + 门票{ticket_cost:.0f} = {total:.0f}元 > 预算{budget:.0f}元"
                )
                suggestions.append(f"建议选择更便宜的交通方式或酒店，或将预算提高到至少{total:.0f}元")

            if total <= budget:
                surplus = budget - total
                suggestions.append(f"预算余量 {surplus:.0f} 元，可适当升级住宿或增加景点")

        # ── 硬检查：景点数量 ──
        itinerary = plan.get("itinerary", [])
        for day in itinerary:
            spots = day.get("attractions", day.get("spots", []))
            if len(spots) > 4:
                issues.append(f"第{day.get('day', '?')}天景点过多（{len(spots)}个）")
                suggestions.append(f"第{day.get('day', '?')}天建议减少到2-3个景点")

        # ── 软检查：LLM 审核 ──
        try:
            soft = self._soft_check(plan)
            issues.extend(soft.get("issues", []))
            suggestions.extend(soft.get("suggestions", []))
        except:
            pass

        return {
            "passed": len([i for i in issues if "预算超标" in i or "景点过多" in i]) == 0,
            "issues": issues,
            "suggestions": suggestions
        }

    def _soft_check(self, plan: dict) -> dict:
        response = self.llm.invoke([
            {"role": "system", "content": SOFT_CHECK_PROMPT},
            {"role": "user", "content": f"行程方案：\n{json.dumps(plan, ensure_ascii=False, indent=2)}\n\n输出JSON。"}
        ])
        try:
            s = response.find("{")
            e = response.rfind("}") + 1
            return json.loads(response[s:e]) if s != -1 else {}
        except:
            return {"issues": [], "suggestions": []}
