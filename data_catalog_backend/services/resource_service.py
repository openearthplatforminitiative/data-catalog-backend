import logging
from http.client import HTTPException
from typing import List, Optional

from geoalchemy2.functions import ST_Covers, ST_Intersects
from geoalchemy2.shape import from_shape
from shapely.geometry.geo import shape
from sqlalchemy import select, case, join, func, and_
import sqlalchemy
from sqlalchemy.orm import aliased

from data_catalog_backend.models import Resource, Provider, SpatialExtent, SpatialExtentRequestType, \
    ResourceType, Category, ResourceCategory
from data_catalog_backend.schemas.resource import ResourceRequest
from data_catalog_backend.schemas.resource_query import ResourceQueryRequest, ResourceQuerySpatialResponse, ResourceQueryResponse
from data_catalog_backend.services.category_service import CategoryService
from data_catalog_backend.services.code_example_service import CodeExampleService
from data_catalog_backend.services.example_service import ExampleService
from data_catalog_backend.services.helpers.resource_queries import ResourceQuery
from data_catalog_backend.services.license_service import LicenseService
from data_catalog_backend.services.provider_service import ProviderService

logger = logging.getLogger(__name__)

class ResourceService:
    def __init__(self, session, license_service: LicenseService, provider_service: ProviderService, category_service: CategoryService, example_service: ExampleService, code_example_service: CodeExampleService):
        self.session = session
        self.license_service = license_service
        self.provider_service = provider_service
        self.category_service = category_service
        self.example_service = example_service
        self.code_example_service = code_example_service

    def find_entity_with_name(self, title) -> Optional[Resource]:
        stmt = select(Resource).where(Resource.title == title)
        return self.session.scalars(stmt).unique().one_or_none()

    def get_resources(self, page: int, per_page: int, resources_req: ResourceQueryRequest):
        base_stmt = (
            select(
                Resource.id.label("id"),
                Resource.title,
                Resource.type,
                Category.icon.label("icon"),
                (Resource.spatial_extent != None).label("has_spatial_extent")
            )
            .select_from(Resource)
            .outerjoin(Resource.spatial_extent)
            .join(ResourceCategory, and_(
                ResourceCategory.c.resource_id == Resource.id,
                ResourceCategory.c.is_main_category.is_(True)
            ))
            .join(Category, Category.id == ResourceCategory.c.category_id)
        )

        query = ResourceQuery()
        base_stmt = query.apply_tag_filters(base_stmt, resources_req)
        base_stmt = query.apply_type_filters(base_stmt, resources_req)
        base_stmt = query.apply_category_filters(base_stmt, resources_req)
        base_stmt = query.apply_provider_filters(base_stmt, resources_req)
        base_stmt = query.apply_spatial_filters(base_stmt, resources_req)
        base_stmt = query.apply_features_filters(base_stmt, resources_req)

        # Remove duplicates
        base_stmt = base_stmt.group_by(Resource.id, Resource.title, Resource.type, Category.icon, SpatialExtent.type, SpatialExtent.geometry)

        # Paginate after counting
        total_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.session.execute(total_stmt).scalar()

        # Pagination
        stmt = base_stmt.offset(per_page * page).limit(per_page)
        results = self.session.execute(stmt).mappings().all()

        return ResourceQueryResponse(
            current_page=page,
            total_pages=total // per_page + (total % per_page > 0),
            resources=[ResourceQuerySpatialResponse(**dict(row)) for row in results]
        )

    def get_resource(self, resource_id) -> Resource:
        stmt = select(Resource).where(Resource.id == resource_id)
        return self.session.scalars(stmt).unique().one_or_none()

    def create_resource(self, resource_req: ResourceRequest) -> Resource:

        license = self.license_service.get_license(resource_req.license)
        if not license:
            raise HTTPException(status_code=404, detail="License not found")

        providers = []
        for provider_id in resource_req.providers:
            provider = self.provider_service.get_provider(provider_id)
            if not provider:
                raise HTTPException(status_code=404, detail="Provider not found")
            providers.append(provider)

        main_category = self.category_service.get_category(resource_req.main_category_id)
        if not main_category:
            raise HTTPException(status_code=404, detail="Main category not found")
        additional_categories = []
        for category_id in resource_req.additional_categories:
            cat = self.category_service.get_category(category_id)
            if not cat:
                raise HTTPException(status_code=404, detail="Category not found")
            additional_categories.append(cat)

        examples = []
        if resource_req.examples:
            examples = self.example_service.create_examples(resource_req.examples)

        code_examples = []
        if resource_req.code_examples:
            code_examples = self.code_example_service.create_code_examples(resource_req.code_examples)

        spatial_extent_objects = []
        if resource_req.spatial_extent is not None:
            for extent in resource_req.spatial_extent:
                spa = SpatialExtent(
                    type=extent.type,
                    region=extent.region if extent.region else None,
                    details=extent.details if extent.details else None,
                    spatial_resolution=extent.spatial_resolution
                )
                if extent.geometry:
                    spa.geom = extent.geometry
                spatial_extent_objects.append(spa)

        resource = Resource(
            **resource_req.model_dump(exclude={
                "examples",
                "license",
                "spatial_extent",
                "code_examples",
                "providers",
                "main_category_id",
                "additional_categories"
            }),
        )
        categories = additional_categories
        resource.categories = categories

        resource.providers = providers
        resource.license = license
        resource.spatial_extent = spatial_extent_objects
        resource.examples = examples
        resource.code_examples = code_examples

        self.session.add(resource)
        try:
            self.session.flush()
            self.session.execute(
                ResourceCategory.insert().values(
                    resource_id=resource.id,
                    category_id=main_category.id,
                    is_main_category=True
                )
            )
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return resource