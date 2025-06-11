import logging
import uuid
from typing import List

from sqlalchemy import select

from data_catalog_backend.models import License
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.license import LicenseRequest

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

    def create_license(self, license: LicenseRequest, user: User) -> License:
        new_license = License(
            name=license.name, url=str(license.url), created_by=user.email
        )
        self.session.add(new_license)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return new_license

    def delete_license(self, license_id: uuid.UUID, user: User):
        license = self.get_license(license_id)
        if not license:
            raise ValueError(f"License with ID {license_id} does not exist.")

        self.session.delete(license)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
