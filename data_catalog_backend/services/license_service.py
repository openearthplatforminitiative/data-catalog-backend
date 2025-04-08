import logging
from typing import Union

from fastapi import HTTPException
from sqlalchemy import select

from data_catalog_backend.models import License
from data_catalog_backend.schemas.license import LicenseRequest, LicenseGetRequest

logger = logging.getLogger(__name__)

class LicenseService: 
    def __init__(self, session):
        self.session = session

    def get_license(self, id) -> License:
        stmt = select(License).where(License.id == id)
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

    def create_or_find_license(self, license: Union[LicenseGetRequest, LicenseRequest]) -> License:
        if license.id:
            existing_license = self.get_license(license.id)
            if existing_license:
                return existing_license
        return self.create_license(license)
