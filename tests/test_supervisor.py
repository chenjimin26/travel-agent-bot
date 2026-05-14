"""测试 Supervisor 参数校验"""
import pytest
from app.agents.supervisor import TravelIntent


class TestTravelIntent:
    def test_all_valid(self):
        i = TravelIntent(destination="北京", departure="沈阳", start_date="2026-05-15", days=3, num_people=2)
        assert i.is_valid is True
        assert i.missing_fields == []

    def test_missing_city(self):
        i = TravelIntent(departure="沈阳", start_date="2026-05-15", days=3, num_people=2)
        assert i.is_valid is False
        assert "目的地" in i.missing_fields

    def test_missing_date(self):
        i = TravelIntent(destination="北京", departure="沈阳", days=3, num_people=2)
        assert i.is_valid is False
        assert any("日期" in m for m in i.missing_fields)

    def test_missing_departure(self):
        i = TravelIntent(destination="北京", start_date="2026-05-15", days=3, num_people=2)
        assert i.is_valid is False
        assert "出发地" in i.missing_fields

    def test_missing_people(self):
        i = TravelIntent(destination="北京", departure="沈阳", start_date="2026-05-15", days=3)
        assert i.is_valid is False
        assert "人数" in i.missing_fields

    def test_missing_days(self):
        i = TravelIntent(destination="北京", departure="沈阳", start_date="2026-05-15", num_people=2)
        assert i.is_valid is False
        assert "旅行天数" in i.missing_fields

    def test_all_missing(self):
        i = TravelIntent()
        assert i.is_valid is False
        assert len(i.missing_fields) >= 4
