import logging
from typing import List, Optional
from pydantic import parse_obj_as, TypeAdapter

from geoalchemy2.functions import ST_Covers, ST_Intersects
from geoalchemy2.shape import from_shape
from shapely.geometry.geo import shape
from sqlalchemy import select, case, join
import sqlalchemy

from data_catalog_backend.models import License, Resource, Provider, SpatialExtent, SpatialExtentRequestType, \
    ResourceType, Category, ResourceCategory
from data_catalog_backend.schemas.resource import ResourcesRequest, ResourcesResponse, ExtraResponse
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

    def get_resources(self, page: int, per_page: int, resources_req: ResourcesRequest):
        first_category = (
            select(Category.icon.label("icon"), ResourceCategory.c.resource_id)
            .select_from(Category)
            .outerjoin(ResourceCategory, Category.id == ResourceCategory.c.category_id)
            .distinct(ResourceCategory.c.resource_id)
            .subquery()
        )

        stmt = select(
            Resource.id,
            Resource.title,
            Resource.type,
            first_category.c.icon.label("icon"),
        ).outerjoin(first_category, Resource.id == first_category.c.resource_id)

        if len(resources_req.tags) > 0:
            tag_filters = []
            for tag in resources_req.tags:
                tag_filters.append(
                    sqlalchemy.or_(
                        Resource.title.ilike(f"%{tag}%"),
                        Resource.abstract.ilike(f"%{tag}%"),
                        Resource.keywords.any(tag),
                        Resource.html_content.ilike(f"%{tag}%"),
                        Resource.spatial_extent.any(SpatialExtent.details.ilike(f"%{tag}%")),
                        Resource.spatial_extent.any(SpatialExtent.region.ilike(f"%{tag}%")),
                    )
                )
            stmt = stmt.where(sqlalchemy.or_(*tag_filters))

        stmt = stmt.add_columns(
            (Resource.spatial_extent != None).label("has_spatial_extent")
        )

        if len(resources_req.features) > 0 or (
            len(resources_req.spatial) > 0 and not (
                len(resources_req.spatial) == 1 and SpatialExtentRequestType.NonSpatial in resources_req.spatial
            )
        ):
            stmt = stmt.outerjoin(Resource.spatial_extent)

        if len(resources_req.features) > 0:
            logging.info("Filtering by features")
            shapely_geoms = [from_shape(shape(feature.geometry), srid=4326) for feature in resources_req.features]
            covers_conditions = [ST_Covers(SpatialExtent.geometry, geom) for geom in shapely_geoms]
            intersects_conditions = [ST_Intersects(SpatialExtent.geometry, geom) for geom in shapely_geoms]

            stmt = stmt.add_columns(
                case(
                    (SpatialExtent.type == SpatialExtentRequestType.Global, True),
                    (sqlalchemy.or_(*covers_conditions), True),
                    else_=False
                ).label("covers_some"),
                case(
                    (SpatialExtent.type == SpatialExtentRequestType.Global, True),
                    (sqlalchemy.and_(*covers_conditions), True),
                    else_=False
                ).label("covers_all"),
                case(
                    (SpatialExtent.type == SpatialExtentRequestType.Global, True),
                    (sqlalchemy.or_(*intersects_conditions), True),
                    else_=False
                ).label("intersects_some"),
                case(
                    (SpatialExtent.type == SpatialExtentRequestType.Global, True),
                    (sqlalchemy.and_(*intersects_conditions), True),
                    else_=False
                ).label("intersects_all")
            )
        if len(resources_req.spatial) > 0:
            logging.info("Filtering by spatial extent types")
            conditions = []
            if SpatialExtentRequestType.NonSpatial in resources_req.spatial:
                conditions.append(Resource.spatial_extent == None)
            other_types = [stype for stype in resources_req.spatial if stype != SpatialExtentRequestType.NonSpatial]
            if other_types:
                conditions.append(
                    SpatialExtent.type.in_(other_types)
                )
            if conditions:
                stmt = stmt.where(
                    sqlalchemy.or_(*conditions)
                )
        if len(resources_req.types) > 0:
            logging.info("Filtering by types")
            logging.info(resources_req.types)
            logging.info(ResourceType.__members__)
            stmt = stmt.where(Resource.type.in_(resources_req.types))
        if len(resources_req.categories) > 0:
            logging.info("Filtering by categories")
            stmt = stmt.outerjoin(Resource.categories)
            stmt = stmt.where(Category.id.in_(resources_req.categories))
        if len(resources_req.providers) > 0:
            logging.info("Filtering by providers")
            stmt = stmt.outerjoin(Resource.providers)
            stmt = stmt.where(Provider.id.in_(resources_req.providers))
        if len(resources_req.features) > 0:
            logging.info("Filtering by features")
            stmt = stmt.where(
                sqlalchemy.or_(
                    (SpatialExtent.type == SpatialExtentRequestType.Global),
                    *intersects_conditions,
                    *covers_conditions
                )
            )
        # get number of rows in total in stmt
        total = self.session.execute(stmt.with_only_columns(sqlalchemy.func.count())).scalar()
        stmt = stmt.offset(per_page * page).limit(per_page)
        resources = self.session.execute(stmt).mappings().all()
        resources_models = [ExtraResponse(**dict(row)) for row in resources]

        return ResourcesResponse(
            current_page=page,
            total_pages=total // per_page + (total % per_page > 0),
            resources=resources_models
        )
    
    def get_resource(self, resource_id) -> Resource:
        stmt = select(Resource).where(Resource.id == resource_id)
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
