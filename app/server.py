from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.chat import router as chat_router

app = FastAPI(
    title="Travel RAG Bot API",
    description="旅游景点问答机器人",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {"service": "Travel RAG Bot API", "version": "1.0.0", "docs": "/docs"}