import json
import os
from typing import List, Dict


def load_city(city_name: str, data_dir: str = "./data/attractions") -> List[Dict]:
    """读取指定城市的景点"""
    filepath = os.path.join(data_dir, f"{city_name}.json")
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        city_data = json.load(f)

    city = city_data.get('city', city_name)
    attractions = city_data.get("attractions", [])
    # 清洗
    for attr in attractions:
        attr['city'] = city
        attr['id'] = f"{city_name}_{attr.get('id', '')}"
        attr.setdefault('open_time', '08:00-18:00')
        attr.setdefault('ticket', '请咨询景区')
        attr.setdefault('best_season', '四季皆宜')
        attr.setdefault('tags', ['景点'])

    return attractions
