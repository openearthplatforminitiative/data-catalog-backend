import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from data_catalog_backend.config import settings
from data_catalog_backend.routes.resource_routes import router as resource_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application")
    yield


def get_application() -> FastAPI:
    api = FastAPI(lifespan=lifespan, root_path=settings.api_root_path)
    api.include_router(resource_routes)
    logging.basicConfig(level=logging.INFO)
    Instrumentator().instrument(api).expose(api)
    return api


app = get_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "data_catalog_backend.__main__:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
    # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
