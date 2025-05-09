import logging
from typing import List

from sqlalchemy import select

from data_catalog_backend.models import License

logger = logging.getLogger(__name__)


class LicenseService:
    def __init__(self, session):
        self.session = session

    def get_license(self, id) -> License:
        stmt = select(License).where(License.id == id)
        return self.session.scalars(stmt).unique().one_or_none()

    def get_license_by_name(self, name: str) -> License:
        stmt = select(License).where(License.name == name)
        return self.session.scalars(stmt).unique().one_or_none()

    def get_licenses(self) -> List[License]:
        stmt = select(License)
        return self.session.scalars(stmt).unique().all()

    def create_license(self, license: License) -> License:
        license = License(name=license.name, url=str(license.url))
        self.session.add(license)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return license
