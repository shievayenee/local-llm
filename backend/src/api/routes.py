from fastapi import APIRouter, HTTPException, status

from models.schemas import ChatRequest, ChatResponse, HealthResponse
from services.ollama_client import generate_chat_completion

router = APIRouter(prefix="/v1", tags=["api"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = await generate_chat_completion(
            messages=request.messages, model=request.model
        )
    except Exception as exc:  # broad to surface upstream errors cleanly
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ollama completion failed: {exc}",
        ) from exc

    return ChatResponse.model_validate(result)
