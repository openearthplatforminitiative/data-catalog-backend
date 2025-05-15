import logging
import logging.config

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from data_catalog_backend import migrate
from data_catalog_backend.config import settings
from data_catalog_backend.routes.admin import router as admin_router
from data_catalog_backend.routes.v1 import router as public_router

logging.config.dictConfig(settings.logging_config)
logger = logging.getLogger(__name__)
logger.info(f"LogLevel is set to {settings.log_level}")
logger.info(f"Starting public api: {settings.include_public_api}")
logger.info(f"Starting admin api: {settings.include_admin_api}")


def get_application() -> FastAPI:
    api = FastAPI(root_path=settings.api_root_path)
    if settings.include_admin_api:
        api.include_router(admin_router)

    if settings.include_public_api:
        api.include_router(public_router)

    logging.basicConfig(level=logging.INFO)
    Instrumentator().instrument(api).expose(api, include_in_schema=False)

    return api


if settings.run_migrations:
    migrate.run_migrations(
        schemas=[settings.postgres_schema],
        connection_string=settings.database_connection,
        script_location=settings.alembic_directory,
        alembic_file=settings.alembic_file,
    )

app = get_application()

if __name__ == "__main__" and (
    settings.include_admin_api or settings.include_public_api
):
    import uvicorn

    uvicorn.run(
        "data_catalog_backend.__main__:app",
        host=settings.uvicorn_host,
        port=settings.uvicorn_port,
        reload=settings.uvicorn_reload,
    )
