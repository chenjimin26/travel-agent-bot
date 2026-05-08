import json
import os
from typing import List, Dict

from app.data.data_loader import load_city


def chunk_one_city(city_name: str, data_dir: str = "./data/attractions") -> List[Dict]:
    attractions = load_city(city_name, data_dir)
    
    chunks = []
    for attr in attractions:
        chunk = {
            "id": attr.get('id'),
            "content": f"{attr.get('name', '')}: {attr.get('description', '')}",
            "metadata": {
                "city": attr.get('city'),
                "name": attr.get('name'),
                "tags": attr.get('tags'),
                "open_time": attr.get('open_time'),
                "ticket": attr.get('ticket'),
                "best_season": attr.get('best_season')
            }
        }
        chunks.append(chunk)
    
    return chunks