from fastapi import APIRouter

from data_catalog_backend.routes.admin.category_routes import router as category_router
from data_catalog_backend.routes.admin.license_routes import router as license_router
from data_catalog_backend.routes.admin.provider_routes import router as provider_router
from data_catalog_backend.routes.admin.resource_routes import router as resource_router
from data_catalog_backend.routes.admin.resourcerelation_routes import (
    router as resource_relation_router,
)
from data_catalog_backend.routes.admin.geometry_routes import router as geometry_router

router = APIRouter(prefix="/admin")
router.include_router(category_router)
router.include_router(license_router)
router.include_router(provider_router)
router.include_router(resource_router)
router.include_router(resource_relation_router)
router.include_router(geometry_router)
