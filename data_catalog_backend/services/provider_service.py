import logging
from typing import List
import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import select

from data_catalog_backend.models import Resource, Provider
from data_catalog_backend.utils import type_mapping


logger = logging.getLogger(__name__)


class ProviderService:
    def __init__(self, session):
        self.session = session

    
    def get_resource_summery_on_id(self, resource_id: uuid.UUID) -> List[dict]:
        from data_catalog_backend.dependencies import get_resource_service
        resource_service = get_resource_service()
        return resource_service.get_resource_summery_on_id(resource_id)

    def get_providers(self) -> List[Provider]:
        stmt = select(Provider)
        return self.session.scalars(stmt).unique().all()

    def get_provider(self, provider_id) -> Provider:
        stmt = select(Provider).where(Provider.provider_id == provider_id)
        return self.session.scalars(stmt).unique().one_or_none() 

    def create_provider(self, provider: Provider) -> Provider:
        associated_resources = []
        for resource_summary in provider.resources:
            resource = self.session.get(Resource, resource_summary["resource_id"])
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