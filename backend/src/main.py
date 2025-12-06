import uvicorn

from core.app import create_app
from config.settings import settings

app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
