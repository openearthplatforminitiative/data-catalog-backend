import logging
from typing import List
import uuid

from sqlalchemy import select

from data_catalog_backend.models import Provider, ResourceProvider
from data_catalog_backend.schemas.User import User

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

    def get_providers_by_resource_id(self, resource_id) -> list[Provider]:
        stmt = (
            select(Provider)
            .select_from(ResourceProvider)
            .join(Provider, ResourceProvider.provider_id == Provider.id)
            .where(
                ResourceProvider.resource_id == resource_id,
            )
        )
        providers = self.session.execute(stmt).scalars().all()
        return [
            Provider(
                id=provider.id,
                name=provider.name,
                short_name=provider.short_name,
                provider_url=provider.provider_url,
                description=provider.description,
            )
            for provider in providers
        ]

    def get_provider_by_short_name(self, short_name: str) -> Provider:
        stmt = select(Provider).where(Provider.short_name == short_name)
        return self.session.scalars(stmt).unique().one_or_none()

    def get_provider(self, id) -> Provider:
        stmt = select(Provider).where(Provider.id == id)
        return self.session.scalars(stmt).unique().one_or_none()

    def create_provider(self, provider: Provider, user: User) -> Provider:
        provider.created_by = user.email
        self.session.add(provider)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return provider

    def update_provider(self, provider_id, provider: Provider, user: User) -> Provider:
        existing_provider = self.get_provider(provider_id)
        if not existing_provider:
            raise ValueError("Provider not found")

        for field, value in vars(provider).items():
            setattr(provider, field, value)

        provider.updated_by = user.email

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return provider

    def delete_provider(self, provider_id: uuid.UUID):
        provider = self.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Provider with id {provider_id} not found")

        try:
            self.session.delete(provider)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
