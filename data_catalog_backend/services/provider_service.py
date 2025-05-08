import logging
from typing import List, Union
import uuid

from fastapi import HTTPException
from sqlalchemy import select

from data_catalog_backend.models import Provider

logger = logging.getLogger(__name__)


class ProviderService:
    def __init__(self, session):
        self.session = session

    def get_resource_summery_on_id(self, id: uuid.UUID) -> List[dict]:
        from data_catalog_backend.dependencies import get_resource_service

        resource_service = get_resource_service()
        return resource_service.get_resource_summery_on_id(id)

    def get_providers(self) -> List[Provider]:
        stmt = select(Provider)
        return self.session.scalars(stmt).unique().all()

    def get_provider_by_short_name(self, short_name: str) -> Provider:
        stmt = select(Provider).where(Provider.short_name == short_name)
        return self.session.scalars(stmt).unique().one_or_none()

    def get_provider(self, id) -> Provider:
        stmt = select(Provider).where(Provider.id == id)
        return self.session.scalars(stmt).unique().one_or_none()

    def create_provider(self, provider: Provider) -> Provider:
        self.session.add(provider)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return provider

    def update_provider(self, id, provider_req):
        provider = self.get_provider(id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        for field, value in provider_req.model_dump().items():
            setattr(provider, field, value)

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return provider
