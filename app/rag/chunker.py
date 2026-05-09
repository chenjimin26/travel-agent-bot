import json
import os
from typing import List
from langchain_core.documents import Document
from app.data.data_loader import load_city


def chunk_one_city(city_name: str, data_dir: str = "./data/attractions") -> List[Document]:
    attractions = load_city(city_name, data_dir)

    docs = []
    for attr in attractions:
        content = f"""景点名称：{attr.get('name', '')}
所在城市：{attr.get('city', '')}
门票价格：{attr.get('ticket', '')}
开放时间：{attr.get('open_time', '')}
最佳游览季节：{attr.get('best_season', '')}
景点标签：{', '.join(attr.get('tags', []))}
景点介绍：{attr.get('description', '')}"""

        doc = Document(
            page_content=content,
            metadata={
                "city": attr.get('city'),
                "name": attr.get('name'),
                "tags": attr.get('tags'),
                "open_time": attr.get('open_time'),
                "ticket": attr.get('ticket'),
                "best_season": attr.get('best_season'),
                "attraction_id": attr.get('id')
            }
        )
        docs.append(doc)

    return docs