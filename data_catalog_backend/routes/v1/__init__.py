from fastapi import APIRouter
from data_catalog_backend.routes.v1.category_routes import router as category_router
from data_catalog_backend.routes.v1.license_routes import router as license_router
from data_catalog_backend.routes.v1.provider_routes import router as provider_router
from data_catalog_backend.routes.v1.resource_routes import router as resource_router

router = APIRouter(prefix="/v1")
router.include_router(category_router)
router.include_router(license_router)
router.include_router(provider_router)
router.include_router(resource_router)
