from fastapi.params import Depends
from sqlalchemy.orm import Session

from data_catalog_backend.database import SessionLocal
from data_catalog_backend.services.examples_service import ExamplesService
from data_catalog_backend.services.provider_service import ProviderService
from data_catalog_backend.services.resource_service import ResourceService
from data_catalog_backend.services.license_service import LicenseService


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_provider_service(
        db: Session = Depends(get_db)
) -> ProviderService:
    return ProviderService(db)

def get_license_service(
        db: Session = Depends(get_db)
) -> LicenseService:
    return LicenseService(db)

def get_examples_service(
        db: Session = Depends(get_db)
) -> ExamplesService:
    return ExamplesService(db)

def get_resource_service(
        db: Session = Depends(get_db),
        license_service: LicenseService = Depends(get_license_service),
        provider_service: ProviderService = Depends(get_provider_service)
) -> ResourceService:
    return ResourceService(db, license_service, provider_service)
