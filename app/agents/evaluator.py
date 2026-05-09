"""
Evaluator Agent — 闭环审核

检查行程的合理性：
- 预算是否超支
- 每天景点数量是否合理
- 格式是否符合要求

返回通过/不通过 + 修改建议。
"""
from app.llm.qwen_client import get_llm


EVALUATOR_PROMPT = """你是旅行方案审核员。检查行程是否存在问题。

输出 JSON：
{
  "passed": true/false,
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"]
}

检查项：
1. 总门票是否超过预算（预算>0时）
2. 每天景点数是否合理（2-3个最佳，不超过4个）
3. 是否有时间冲突（开放时间与行程安排）
4. 格式是否完整（有itinerary、total_ticket、tips）"""


class EvaluatorAgent:
    def __init__(self):
        self.llm = get_llm("deepseek")

    def evaluate(self, plan: dict, budget: float = 0) -> dict:
        import json

        messages = [
            {"role": "system", "content": EVALUATOR_PROMPT},
            {"role": "user", "content": f"预算限制：{budget}元（0=不限）\n\n行程方案：\n{json.dumps(plan, ensure_ascii=False, indent=2)}\n\n请审核，输出JSON。"}
        ]
        response = self.llm.invoke(messages)

        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            data = json.loads(response[start:end]) if start != -1 else {}
        except:
            data = {"passed": False, "issues": ["审核解析失败"], "suggestions": ["请重新生成行程计划"]}

        return data
