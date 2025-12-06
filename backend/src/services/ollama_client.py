from typing import Dict, List, Optional

from ollama import AsyncClient, ResponseError

from config.settings import settings
from models.schemas import ChatMessage


async def _ensure_model(client: AsyncClient, model: str) -> None:
    """
    Pull the model if it's missing. Some client versions return an async iterator,
    others return a coroutine; handle both.
    """
    pull_result = client.pull(model=model)

    if hasattr(pull_result, "__aiter__"):
        async for chunk in pull_result:
            if chunk.get("status") == "success":
                return
    else:
        result = await pull_result
        if isinstance(result, dict) and result.get("status") == "success":
            return

    raise RuntimeError(f"Failed to pull model '{model}' from Ollama")


async def _chat_once(client: AsyncClient, model: str, payload: List[Dict]) -> Dict:
    return await client.chat(model=model, messages=payload, stream=False)


async def generate_chat_completion(
    messages: List[ChatMessage], model: Optional[str] = None
) -> Dict:
    """
    Send chat history to a local Ollama model and return the assistant reply.
    If the model is missing, it will be pulled once and retried.
    """
    client = (
        AsyncClient(host=settings.ollama_api_url)
        if settings.ollama_api_url
        else AsyncClient()
    )

    selected_model = model or settings.ollama_model
    payload = [{"role": m.role, "content": m.content} for m in messages]

    try:
        response = await _chat_once(client, selected_model, payload)
    except ResponseError as exc:
        if getattr(exc, "status_code", None) == 404:
            await _ensure_model(client, selected_model)
            response = await _chat_once(client, selected_model, payload)
        else:
            raise

    return {
        "model": response["model"],
        "message": {
            "role": response["message"]["role"],
            "content": response["message"]["content"],
        },
    }
