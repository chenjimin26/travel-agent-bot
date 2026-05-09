from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="用户消息")
    session_id: str | None = Field(default=None, description="会话ID")
    mode: str = Field(default="fast", description="查询模式: fast(快速) / precision(精度)")


class ChatResponse(BaseModel):
    message: str = Field(description="助手回复")
    sources: list = Field(default=[], description="召回的景点列表")


class HealthResponse(BaseModel):
    status: str = Field(description="服务状态")
    version: str = Field(description="版本号")
    attractions_count: int = Field(description="景点数量")


class ErrorResponse(BaseModel):
    detail: str = Field(description="错误详情")