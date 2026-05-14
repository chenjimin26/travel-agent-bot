"""测试天气工具"""
from app.tools.weather import get_weather, _translate_weather


class TestWeather:
    def test_get_weather_beijing(self):
        r = get_weather("北京")
        assert "天气" in r
        assert "°C" in r

    def test_get_weather_with_date(self):
        r = get_weather("北京", "2026-05-12", 2)
        assert "2026-05-12" in r

    def test_far_future_date(self):
        r = get_weather("北京", "2027-06-15", 3)
        assert "天气" in r  # 不管有没有数据，至少不崩

    def test_translate_sunny(self):
        assert "晴" in _translate_weather("Sunny")

    def test_translate_rain(self):
        assert "雨" in _translate_weather("Moderate rain")

    def test_translate_unknown(self):
        assert _translate_weather("Tornado") == "Tornado"
