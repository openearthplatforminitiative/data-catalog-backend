import logging
from typing import Optional

from sqlalchemy import select, func, and_

from data_catalog_backend.models import (
    Resource,
    SpatialExtent,
    Category,
    ResourceCategory,
    ResourceProvider,
)
from data_catalog_backend.schemas.resource import (
    ResourceRequest,
)
from data_catalog_backend.schemas.resource_query import (
    ResourceQueryRequest,
    ResourceQuerySpatialResponse,
    ResourceQueryResponse,
)
from data_catalog_backend.services.category_service import CategoryService
from data_catalog_backend.services.code_example_service import CodeExampleService
from data_catalog_backend.services.example_service import ExampleService
from data_catalog_backend.services.helpers.resource_queries import ResourceQuery
from data_catalog_backend.services.license_service import LicenseService
from data_catalog_backend.services.provider_service import ProviderService

logger = logging.getLogger(__name__)


class ResourceService:
    def __init__(
        self,
        session,
        license_service: LicenseService,
        provider_service: ProviderService,
        category_service: CategoryService,
        example_service: ExampleService,
        code_example_service: CodeExampleService,
    ):
        self.session = session
        self.license_service = license_service
        self.provider_service = provider_service
        self.category_service = category_service
        self.example_service = example_service
        self.code_example_service = code_example_service

    def find_entity_with_name(self, title) -> Optional[Resource]:
        stmt = select(Resource).where(Resource.title == title)
        return self.session.scalars(stmt).unique().one_or_none()

    def get_resources(
        self, page: int, per_page: int, resources_req: ResourceQueryRequest
    ):
        base_stmt = (
            select(
                Resource.id.label("id"),
                Resource.title,
                Resource.type,
                Category.icon.label("icon"),
                (Resource.spatial_extent != None).label("has_spatial_extent"),
            )
            .select_from(Resource)
            .outerjoin(Resource.spatial_extent)
            .join(
                ResourceCategory,
                and_(
                    ResourceCategory.resource_id == Resource.id,
                    ResourceCategory.is_main_category.is_(True),
                ),
            )
            .join(Category, Category.id == ResourceCategory.category_id)
        )

        query = ResourceQuery()
        base_stmt = query.apply_tag_filters(base_stmt, resources_req)
        base_stmt = query.apply_type_filters(base_stmt, resources_req)
        base_stmt = query.apply_category_filters(base_stmt, resources_req)
        base_stmt = query.apply_provider_filters(base_stmt, resources_req)
        base_stmt = query.apply_spatial_filters(base_stmt, resources_req)
        base_stmt = query.apply_features_filters(base_stmt, resources_req)

        base_stmt = base_stmt.group_by(
            Resource.id,
            Resource.title,
            Resource.type,
            Category.icon,
            SpatialExtent.type,
            SpatialExtent.geometry,
        )
        base_stmt = base_stmt.distinct(Resource.id)

        total_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.session.execute(total_stmt).scalar()

        # Pagination
        stmt = base_stmt.offset(per_page * page).limit(per_page)
        results = self.session.execute(stmt).mappings().all()

        return ResourceQueryResponse(
            current_page=page,
            total_pages=total // per_page + (total % per_page > 0),
            data=[ResourceQuerySpatialResponse(**dict(row)) for row in results],
        )

    def get_resource(self, resource_id) -> Resource:
        stmt = select(Resource).where(Resource.id == resource_id)
        return self.session.scalars(stmt).unique().one_or_none()

    def create_resource(self, resource_req: ResourceRequest) -> Resource:
        try:
            license = self.license_service.get_license_by_name(resource_req.license)
            if not license:
                raise ValueError("License not found")

            providers = []
            for provider_short_name in resource_req.providers:
                provider = self.provider_service.get_provider_by_short_name(
                    provider_short_name
                )
                if not provider:
                    raise ValueError("Provider not found")
                providers.append(ResourceProvider(role="", provider=provider))

            main_category = self.category_service.get_category_by_title(
                resource_req.main_category
            )
            if not main_category:
                raise ValueError("Main category not found")

            categories = [
                ResourceCategory(is_main_category=True, category=main_category)
            ]
            if resource_req.additional_categories:
                for category_title in resource_req.additional_categories:
                    cat = self.category_service.get_category_by_title(category_title)
                    if not cat:
                        raise ValueError("Category not found")
                    categories.append(
                        ResourceCategory(is_main_category=False, category=cat)
                    )

            examples = []
            if resource_req.examples:
                examples = self.example_service.create_examples(resource_req.examples)

            code_examples = []
            if resource_req.code_examples:
                code_examples = self.code_example_service.create_code_examples(
                    resource_req.code_examples
                )

            spatial_extent_objects = []
            if resource_req.spatial_extent is not None:
                for extent in resource_req.spatial_extent:
                    spa = SpatialExtent(
                        type=extent.type,
                        region=extent.region if extent.region else None,
                        details=extent.details if extent.details else None,
                        spatial_resolution=extent.spatial_resolution,
                    )
                    if extent.geometry:
                        spa.geom = extent.geometry
                    spatial_extent_objects.append(spa)

            keywords = []
            if resource_req.keywords is not None:
                for keyword in resource_req.keywords:
                    keywords.append(keyword.strip())

            resource = Resource(
                **resource_req.model_dump(
                    exclude={
                        "examples",
                        "license",
                        "spatial_extent",
                        "code_examples",
                        "providers",
                        "main_category",
                        "additional_categories",
                        "keywords",
                    }
                ),
            )
            categories = categories
            resource.categories = categories

            resource.providers = providers
            resource.license = license
            resource.spatial_extent = spatial_extent_objects
            resource.examples = examples
            resource.code_examples = code_examples
            resource.keywords = keywords

            self.session.add(resource)
            self.session.commit()

            return resource
        except HTTPException as http_exc:
            # Log and re-raise HTTP exceptions
            logger.error(f"HTTP error: {http_exc.detail}")
            raise
        except Exception as e:
            # Log unexpected errors and raise a 500 error
            logger.error(f"Unexpected error: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while creating the resource",
            )
