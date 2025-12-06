from fastapi import FastAPI

from api.routes import router as api_router
from config.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.include_router(api_router, prefix="/api")
    return app
