from typing import AsyncGenerator, Dict, List, Optional

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


async def _chat_stream(
    client: AsyncClient, model: str, payload: List[Dict]
) -> AsyncGenerator[str, None]:
    """
    Yield content chunks from Ollama. Handles client implementations that return
    an async generator directly or a coroutine that needs awaiting.
    """
    stream_obj = client.chat(model=model, messages=payload, stream=True)

    async def iterate(obj):
        if hasattr(obj, "__aiter__"):
            async for chunk in obj:
                content = chunk.get("message", {}).get("content")
                if content:
                    yield content
        else:
            awaited = await obj
            if hasattr(awaited, "__aiter__"):
                async for chunk in awaited:
                    content = chunk.get("message", {}).get("content")
                    if content:
                        yield content
            elif isinstance(awaited, list):
                for chunk in awaited:
                    content = (
                        chunk.get("message", {}).get("content")
                        if isinstance(chunk, dict)
                        else None
                    )
                    if content:
                        yield content
            elif isinstance(awaited, dict):
                content = awaited.get("message", {}).get("content")
                if content:
                    yield content

    async for chunk in iterate(stream_obj):
        yield chunk


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


async def stream_chat_completion(
    messages: List[ChatMessage], model: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """
    Stream chat completion text chunks. If model missing, pull and retry once.
    """
    client = (
        AsyncClient(host=settings.ollama_api_url)
        if settings.ollama_api_url
        else AsyncClient()
    )
    selected_model = model or settings.ollama_model
    payload = [{"role": m.role, "content": m.content} for m in messages]

    async def stream():
        try:
            async for piece in _chat_stream(client, selected_model, payload):
                yield piece
        except ResponseError as exc:
            if getattr(exc, "status_code", None) == 404:
                await _ensure_model(client, selected_model)
                async for piece in _chat_stream(client, selected_model, payload):
                    yield piece
            else:
                raise

    async for chunk in stream():
        yield chunk
