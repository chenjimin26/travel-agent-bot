"""
天气查询工具 — 用 wttr.in API
"""
import requests


def get_weather(city: str, start_date: str = None, days: int = 3) -> str:
    """查询城市天气。输入：城市名+出发日期。返回出行期间的天气描述。"""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        weather_list = data.get("weather", [])

        # 如果指定了出发日期，只取从该日期开始的天气
        if start_date:
            weather_list = [w for w in weather_list if w["date"] >= start_date]
        weather_list = weather_list[:days]

        results = []
        for w in weather_list:
            d = w["date"]
            high = w["maxtempC"]
            low = w["mintempC"]
            desc = w["hourly"][4]["weatherDesc"][0]["value"]
            # 翻译天气描述
            weather_cn = _translate_weather(desc)
            results.append(f"{d}: {weather_cn} {low}°C~{high}°C")

        return f"{city}天气：\n" + "\n".join(results) if results else f"{city}暂无{start_date or '今日'}起的天气预报（只能查近7天），请临近出发再查"
    except:
        return f"无法获取{city}天气"


def _translate_weather(desc: str) -> str:
    mapping = {
        "Sunny": "☀️晴",
        "Clear": "☀️晴",
        "Partly cloudy": "⛅多云",
        "Cloudy": "☁️阴",
        "Overcast": "☁️阴",
        "Light rain": "🌧小雨",
        "Moderate rain": "🌧中雨",
        "Heavy rain": "🌧大雨",
        "Light drizzle": "🌧毛毛雨",
        "Patchy rain possible": "🌧可能阵雨",
        "Mist": "🌫薄雾",
        "Fog": "🌫大雾",
    }
    return mapping.get(desc, desc)
