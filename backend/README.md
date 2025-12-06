# FastAPI Backend (local LLM)

## Setup
- Install dependencies: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Ensure Ollama is installed locally with your chosen model pulled (default `llama3`), or set `APP_OLLAMA_MODEL`.

## Run
- Dev server: `uvicorn main:app --app-dir backend/src --reload`
- Configure via env vars (optional): `APP_HOST`, `APP_PORT`, `APP_OLLAMA_MODEL`, `APP_OLLAMA_API_URL`.

## API
- `GET /api/v1/health` → `{"status":"ok"}`
- `POST /api/v1/chat` with body:
```json
{
  "messages": [
    {"role": "user", "content": "Hello, who are you?"}
  ],
  "model": "llama3"
}
```
Returns assistant reply from the local Ollama model.
- If the specified model is missing, the backend will auto-pull it from Ollama before retrying the request.
- `POST /api/v1/chat/stream` streams plain text tokens/chunks; send the same body as `/chat`.
