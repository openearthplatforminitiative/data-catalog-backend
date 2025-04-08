import logging
from typing import List, Union
import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import select

from data_catalog_backend.models import Resource, Provider
from data_catalog_backend.schemas.provider import ProviderRequest, ProviderGetRequest
from data_catalog_backend.utils import type_mapping


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

    def get_provider(self, id) -> Provider:
        stmt = select(Provider).where(Provider.id == id)
        return self.session.scalars(stmt).unique().one_or_none() 

    def create_provider(self, provider: Provider) -> Provider:
        associated_resources = []
        for resource_summary in provider.resources:
            resource = self.session.get(Resource, resource_summary["id"])
            if resource:
                associated_resources.append(resource)

        provider.resources = associated_resources
        self.session.add(provider)

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        
        return provider

    def create_or_find_provider(self, provider: Union[ProviderRequest, ProviderGetRequest]) -> Provider:
        existing_provider = self.get_provider(provider.provider_id)
        if existing_provider:
            return existing_provider
        return self.create_provider(provider)

    def update_provider(self, provider_id, provider_req):
        provider = self.get_provider(provider_id)
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
