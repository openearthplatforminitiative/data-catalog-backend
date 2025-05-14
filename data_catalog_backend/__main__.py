import logging
import logging.config

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from data_catalog_backend import migrate
from data_catalog_backend.config import settings
from data_catalog_backend.routes.admin_routes import router as admin_routes
from data_catalog_backend.routes.category_routes import router as category_routes
from data_catalog_backend.routes.license_routes import router as license_routes
from data_catalog_backend.routes.provider_routes import router as provider_routes
from data_catalog_backend.routes.resource_routes import router as resource_routes

logging.config.dictConfig(settings.logging_config)
logger = logging.getLogger(__name__)
logger.info(f"LogLevel is set to {settings.log_level}")


def get_application() -> FastAPI:
    api = FastAPI(root_path=settings.api_root_path)
    api.include_router(resource_routes)
    api.include_router(license_routes)
    api.include_router(provider_routes)
    api.include_router(category_routes)
    api.include_router(admin_routes)
    logging.basicConfig(level=logging.INFO)
    Instrumentator().instrument(api).expose(api, include_in_schema=False)

    return api


app = get_application()

if settings.run_migrations:
    logger.info("Running database migrations")
    migrate.run_migrations(
        schemas=[settings.postgres_schema],
        connection_string=settings.database_connection,
        script_location=settings.alembic_directory,
        alembic_file=settings.alembic_file,
    )

app = get_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "data_catalog_backend.__main__:app",
        host=settings.uvicorn_host,
        port=settings.uvicorn_port,
        reload=settings.uvicorn_reload,
    )
