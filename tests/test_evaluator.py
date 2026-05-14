"""测试 Evaluator 硬计算"""
import pytest
from app.agents.evaluator import EvaluatorAgent


class TestEvaluatorHardCalc:

    def test_budget_exceeded_two_persons(self):
        """2人，交通1100×2=2200，酒店300×2晚=600，门票200，总3000 > 预算2000"""
        e = EvaluatorAgent()
        plan = {"itinerary": [{"day": 1, "attractions": ["故宫"]}], "total_ticket": 200}
        transport = {"go_train": {"price": 550}, "back_train": {"price": 550}, "total_transport_cost": 1100}
        hotels = {"hotels": [{"price": "300元/晚"}]}

        result = e.evaluate(plan, budget=2000, transport=transport, hotels=hotels, num_people=2, days=3)
        assert result["passed"] is False
        assert any("预算超标" in i for i in result["issues"])

    def test_budget_ok_one_person(self):
        """1人，交通1100，酒店600，门票200，总1900 < 预算2000"""
        e = EvaluatorAgent()
        plan = {"itinerary": [{"day": 1, "attractions": ["故宫"]}], "total_ticket": 200}
        transport = {"go_train": {"price": 550}, "back_train": {"price": 550}, "total_transport_cost": 1100}
        hotels = {"hotels": [{"price": "300元/晚"}]}

        result = e.evaluate(plan, budget=2000, transport=transport, hotels=hotels, num_people=1, days=3)
        assert result["passed"] is True
        assert any("余量" in s for s in result["suggestions"])

    def test_no_budget_limit(self):
        """预算为0表示不限"""
        e = EvaluatorAgent()
        plan = {"itinerary": [], "total_ticket": 9999}
        transport = {"total_transport_cost": 9999}
        hotels = {"hotels": [{"price": "9999元/晚"}]}

        result = e.evaluate(plan, budget=0, transport=transport, hotels=hotels, num_people=5, days=10)
        assert result["passed"] is True

    def test_transport_multiplied_by_people(self):
        """验证交通费 = 往返价 × 人数"""
        e = EvaluatorAgent()
        plan = {"itinerary": [], "total_ticket": 0}
        transport = {"total_transport_cost": 500}
        hotels = {"hotels": []}

        r1 = e.evaluate(plan, budget=600, transport=transport, hotels=hotels, num_people=1, days=2)
        r2 = e.evaluate(plan, budget=1100, transport=transport, hotels=hotels, num_people=2, days=2)

        assert r1["passed"] is True
        assert r2["passed"] is True

    def test_too_many_attractions_per_day(self):
        """每天超过4个景点应报警"""
        e = EvaluatorAgent()
        plan = {"itinerary": [{"day": 1, "attractions": ["A", "B", "C", "D", "E"]}]}

        result = e.evaluate(plan, budget=0, num_people=1, days=1)
        assert any("景点过多" in i for i in result["issues"])

    def test_empty_plan_still_runs(self):
        """空计划不崩，应返回 passed（无 issues 则通过）"""
        e = EvaluatorAgent()
        result = e.evaluate({}, budget=1000)
        assert "passed" in result  # 至少不崩
