import logging

from fastapi.params import Depends
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from data_catalog_backend.config import settings
from data_catalog_backend.database import SessionLocal
from data_catalog_backend.services.category_service import CategoryService
from data_catalog_backend.services.code_example_service import CodeExampleService
from data_catalog_backend.services.example_service import ExampleService
from data_catalog_backend.services.geometry_service import GeometryService
from data_catalog_backend.services.license_service import LicenseService
from data_catalog_backend.services.provider_service import ProviderService
from data_catalog_backend.services.resource_relation_service import (
    ResourceRelationService,
)
from data_catalog_backend.services.resource_service import ResourceService


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


def get_provider_service(db: Session = Depends(get_db)) -> ProviderService:
    return ProviderService(db)


def get_license_service(db: Session = Depends(get_db)) -> LicenseService:
    return LicenseService(db)


def get_geometry_service(db: Session = Depends(get_db)) -> GeometryService:
    return GeometryService(db)


def get_examples_service(db: Session = Depends(get_db)) -> ExampleService:
    return ExampleService(db)


def get_code_example_service(db: Session = Depends(get_db)) -> CodeExampleService:
    return CodeExampleService(db)


def get_resource_service(
    db: Session = Depends(get_db),
    license_service: LicenseService = Depends(get_license_service),
    provider_service: ProviderService = Depends(get_provider_service),
    category_service: CategoryService = Depends(get_category_service),
    example_service: ExampleService = Depends(get_examples_service),
    geometry_service: GeometryService = Depends(get_geometry_service),
    code_example_service: CodeExampleService = Depends(get_code_example_service),
) -> ResourceService:
    return ResourceService(
        db,
        license_service,
        provider_service,
        category_service,
        example_service,
        geometry_service,
        code_example_service,
    )


def get_resource_relation_service(
    db: Session = Depends(get_db),
    resource_service: ResourceService = Depends(get_resource_service),
) -> ResourceRelationService:
    return ResourceRelationService(db, resource_service)


def get_jwk_client() -> PyJWKClient:
    return PyJWKClient(settings.auth_jwks_url)
