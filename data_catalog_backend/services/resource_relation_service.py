import logging
from typing import Optional

from sqlalchemy import select

from data_catalog_backend.models import Resource, ResourceResource
from data_catalog_backend.schemas.resource import ResourceRelationRequest

logger = logging.getLogger(__name__)

class ResourceRelationService:
    def __init__(self, session, resource_service):
        self.session = session
        self.resource_service = resource_service

    def create_resource_relation(
        self, resource_relation_req: ResourceRelationRequest
    ) -> ResourceResource:
        based_on_entity = self.resource_service.find_entity_with_name(
            resource_relation_req.based_on
        )
        if not based_on_entity:
            raise ValueError("Based on resource not found")
        used_by_entity = self.resource_service.find_entity_with_name(
            resource_relation_req.used_by
        )
        if not used_by_entity:
            raise ValueError("Used by resource not found")
        resource_relation = ResourceResource(
            used_by=used_by_entity.id,
            based_on=based_on_entity.id,
        )
        self.session.add(resource_relation)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return resource_relation
