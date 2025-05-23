import logging

from data_catalog_backend.models import resource_relation
from data_catalog_backend.schemas.resource import ResourceRelationRequest

logger = logging.getLogger(__name__)


class ResourceRelationService:
    def __init__(self, session, resource_service):
        self.session = session
        self.resource_service = resource_service

    def create_resource_relation(
        self, resource_relation_req: ResourceRelationRequest
    ) -> None:
        parent = self.resource_service.find_entity_with_name(
            resource_relation_req.parent
        )
        if not parent:
            raise ValueError("Parent resource not found")
        child = self.resource_service.find_entity_with_name(resource_relation_req.child)
        if not child:
            raise ValueError("Child resource not found")
        stmt = resource_relation.insert().values(
            parent_id=parent.id,
            child_id=child.id,
        )
        try:
            self.session.execute(stmt)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
