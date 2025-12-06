from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Service health status")


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., description="Natural language content for the role")


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(
        ..., description="Conversation history in chat message format"
    )
    model: Optional[str] = Field(
        default=None, description="Optional override of the default Ollama model"
    )


class ChatResponse(BaseModel):
    model: str = Field(..., description="Model used for the completion")
    message: ChatMessage = Field(..., description="Assistant message response")
