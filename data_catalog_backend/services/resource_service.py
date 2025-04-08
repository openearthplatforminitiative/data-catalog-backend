import logging
from typing import List, Optional

from geoalchemy2.functions import ST_Covers, ST_Intersects
from sqlalchemy import select, case

from data_catalog_backend.models import License, Resource, Provider, SpatialExtent, SpatialExtentRequestType, \
    ResourceType
from data_catalog_backend.schemas.resources import ResourcesRequest
from data_catalog_backend.services.license_service import LicenseService
from data_catalog_backend.services.provider_service import ProviderService

logger = logging.getLogger(__name__)

class ResourceService:
    def __init__(self, session, license_service: LicenseService, provider_service: ProviderService):
        self.session = session
        self.license_service = license_service
        self.provider_service = provider_service

    def find_entity_with_name(self, title) -> Optional[Resource]:
        stmt = select(Resource).where(Resource.title == title)
        return self.session.scalars(stmt).unique().one_or_none()

    def get_resources(self, page: int, per_page: int, resources_req: ResourcesRequest) -> List[Resource]:
        stmt = select(Resource)

        if len(resources_req.features) > 0 or (
            len(resources_req.spatial) > 0 and not (
                len(resources_req.spatial) == 1 and SpatialExtentRequestType.NonSpatial in resources_req.spatial
            )
        ):
            stmt = stmt.outerjoin(Resource.spatial_extent)

        if len(resources_req.features) > 0:
            stmt = stmt.add_columns(
                case((ST_Covers(SpatialExtent.geometry, resources_req.geometry), True), else_=False).label("covers"),
                case((ST_Intersects(SpatialExtent.geometry, resources_req.geometry), True), else_=False).label("intersects")
            )

        if len(resources_req.types) > 0:
            logging.info(resources_req.types)
            logging.info(ResourceType.__members__)
            stmt = stmt.where(Resource.type.in_(resources_req.types))
        if len(resources_req.providers) > 0:
            stmt = stmt.where(Provider.id.in_(resources_req.providers))
        if len(resources_req.features) > 0:
            stmt = stmt.where(
                ST_Intersects(SpatialExtent.geometry, resources_req.geometry) | ST_Covers(SpatialExtent.geometry, resources_req.geometry)
            )
        stmt = stmt.offset(per_page * page).limit(per_page)
        return self.session.scalars(stmt).unique().all()
    
    def get_resource(self, id) -> Resource:
            stmt = select(Resource).where(Resource.id == id)
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

    def update_resource(self, id, resource_req):
        pass
        # resource = self.get_resource(id)
        # if not resource:
        #     raise HTTPException(status_code=404, detail="Resource not found")
        #
        # for field, value in resource_req.model_dump().items():
        #     logger.info(value)
        #     # setattr(resource, field, value)
        #
        # # try:
        # #     self.session.commit()
        # # except Exception as e:
        # #     self.session.rollback()
        # #     raise e
        # #
        # return resource
