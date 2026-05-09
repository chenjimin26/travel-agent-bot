import os
from fastapi import APIRouter
from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


def count_attractions() -> int:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "data", "attractions")
    if not os.path.exists(data_dir):
        return 0
    
    count = 0
    for f in os.listdir(data_dir):
        if f.endswith(".json"):
            path = os.path.join(data_dir, f)
            try:
                import json
                with open(path, encoding="utf-8") as fp:
                    data = json.load(fp)
                    if isinstance(data, dict) and "attractions" in data:
                        count += len(data["attractions"])
            except:
                pass
    return count


def get_db_size() -> float:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, "data", "chroma_db")
    if not os.path.exists(db_path):
        return 0.0
    
    total = 0
    for root, dirs, files in os.walk(db_path):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    return total / (1024 * 1024)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        attractions_count=count_attractions()
    )