import logging

from fastapi import HTTPException
from sqlalchemy import select

from data_catalog_backend.models import License

logger = logging.getLogger(__name__)

class LicenseService: 
    def __init__(self, session):
        self.session = session

    def get_license(self, license_id) -> License:
        stmt = select(License).where(License.license_id == license_id)
        return self.session.scalars(stmt).unique().one_or_none()

    def create_license(self, license: License) -> License:
        license = License(
            name = license.name,
            url=str(license.url),
            description = license.description
        )
        self.session.add(license)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return license      
