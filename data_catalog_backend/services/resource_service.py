import logging
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from data_catalog_backend.models.resource_models import License, Resource
from data_catalog_backend.services.license_service import LicenseService
from data_catalog_backend.services.provider_service import ProviderService
from data_catalog_backend.utils.type_mapping import type_mapping


logger = logging.getLogger(__name__)

class ResourceService:
    def __init__(self, session, license_service: LicenseService, provider_service: ProviderService):
        self.session = session
        self.license_service = license_service
        self.provider_service = provider_service

    def find_entity_with_name(self, title) -> Optional[Resource]:
        stmt = select(Resource).where(Resource.title == title)
        return self.session.scalars(stmt).unique().one_or_none()

    def get_resources(self) -> List[Resource]:
        stmt = select(Resource)
        return self.session.scalars(stmt).unique().all()
    
    def get_resource(self, resource_id) -> Resource: 
            stmt = select(Resource).where(Resource.resource_id == resource_id)
            return self.session.scalars(stmt).unique().one_or_none()
    
    def create_resource(self, resource: Resource) -> Resource:

        license = self.session.query(License).filter(License.name == resource.license.name).first()

        if not license:
            license = self.license_service.create_license(resource.license)

        resource.license = license

        self.session.add(resource)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return resource

    def get_resource_summary_list(self) -> List[Resource]:
        stmt = select(
            Resource.resource_id, 
            Resource.title, 
            Resource.abstract, 
            Resource.type)
        
        result = self.session.execute(stmt).mappings().all()
        return [
            {
                "resource_id": row.resource_id,
                "title": row.title,
                "abstract": row.abstract,
                "type": row.type
            }
            for row in result
        ]

    def get_resource_summery_on_id(self, resource_id) -> List[Resource]:
        stmt = select(
            Resource.resource_id, 
            Resource.title, 
            Resource.abstract, 
            Resource.type).where(Resource.resource_id == resource_id)
        
        result = self.session.scalars(stmt).mappings().all()
        return [
            {
                "resource_id": row.resource_id,
                "title": row.title,
                "abstract": row.abstract,
                "type": row.type
            }
            for row in result
        ]
