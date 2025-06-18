import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func, and_, case
from sqlalchemy.sql.functions import user, current_user

from data_catalog_backend.models import (
    Resource,
    SpatialExtent,
    Category,
    ResourceCategory,
    ResourceProvider,
    ResourceType,
    Examples,
    SpatialExtentType,
    TemporalExtent,
)
from data_catalog_backend.schemas.User import User

from data_catalog_backend.schemas.resource_query import (
    ResourceQueryRequest,
    ResourceQuerySpatialResponse,
    ResourceQueryResponse,
)
from data_catalog_backend.services.category_service import CategoryService
from data_catalog_backend.services.code_example_service import CodeExampleService
from data_catalog_backend.services.example_service import ExampleService
from data_catalog_backend.services.geometry_service import GeometryService
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
        geometry_service: GeometryService,
        code_example_service: CodeExampleService,
    ):
        self.session = session
        self.license_service = license_service
        self.provider_service = provider_service
        self.category_service = category_service
        self.example_service = example_service
        self.geometry_service = geometry_service
        self.code_example_service = code_example_service

    def find_entity_with_name(self, title) -> Optional[Resource]:
        stmt = select(Resource).where(Resource.title == title)
        return self.session.scalars(stmt).unique().one_or_none()

    def get_resources(
        self, page: int, per_page: int, resources_req: ResourceQueryRequest
    ):
        base_stmt = (
            select(
                Resource.id,
                Resource.title,
                Resource.abstract,
                Resource.type,
                Category.icon.label("icon"),
                Resource.has_spatial_extent,
                Resource.spatial_extent_type,
            )
            .select_from(Resource)
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
        base_stmt = query.apply_temporal_filters(base_stmt, resources_req)

        group_by = [
            Resource.id,
            Resource.title,
            Resource.type,
            Category.icon,
            Resource.has_spatial_extent,
            Resource.spatial_extent_type,
        ]
        if resources_req.features and len(resources_req.features) > 0:
            group_by.append(SpatialExtent.id)

        base_stmt = base_stmt.group_by(*group_by)
        base_stmt = base_stmt.distinct(Resource.title)
        base_stmt = base_stmt.order_by(Resource.title)

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

    def get_resource(self, resource_id: uuid.UUID) -> Resource:
        stmt = select(Resource).where(Resource.id == resource_id)
        return self.session.scalars(stmt).unique().one_or_none()

    def create_resource(self, resource_req: Resource, current_user: User) -> Resource:
        try:
            license = self.license_service.get_license_by_name(resource_req.license)
            if not license and resource_req.type is ResourceType.Dataset:
                raise ValueError("License not found and required for Datasets")

            providers = []
            for provider_short_name in resource_req.providers:
                provider = self.provider_service.get_provider_by_short_name(
                    provider_short_name
                )
                if not provider:
                    raise ValueError("Provider not found")
                providers.append(
                    ResourceProvider(
                        role="", provider=provider, created_by=current_user.email
                    )
                )

            main_category = self.category_service.get_main_category(resource_req.id)
            if not main_category:
                raise ValueError("Main category not found")

            categories = [
                ResourceCategory(
                    is_main_category=True,
                    category=main_category,
                    created_by=current_user.email,
                )
            ]
            if resource_req.additional_categories:
                for category_title in resource_req.additional_categories:
                    cat = self.category_service.get_category_by_title(category_title)
                    if not cat:
                        raise ValueError("Category not found")
                    categories.append(
                        ResourceCategory(
                            is_main_category=False,
                            category=cat,
                            created_by=current_user.email,
                        )
                    )

            examples = []
            if resource_req.examples:
                for resource_example in resource_req.examples:
                    examples.append(
                        Examples(
                            title=resource_example.title,
                            type=resource_example.type,
                            description=resource_example.description,
                            example_url=resource_example.example_url,
                            favicon_url=resource_example.favicon_url,
                            created_by=current_user.email,
                        )
                    )

            temporal_extents = []
            if resource_req.temporal_extent:
                for temporal_extent in resource_req.temporal_extent:
                    if not temporal_extent.start_date:
                        raise ValueError("Start date is required in Temporal Extents")
                    temporal_extents.append(
                        TemporalExtent(
                            start_date=temporal_extent.start_date,
                            end_date=temporal_extent.end_date,
                            created_by=current_user.email,
                        )
                    )

            code_examples = []
            if resource_req.code_examples:
                code_examples = self.code_example_service.create_code_examples(
                    resource_req.code_examples, user=current_user
                )

            spatial_extent_objects = []
            if resource_req.spatial_extent is not None:
                for extent in resource_req.spatial_extent:
                    geometries = []
                    if (
                        extent.type == SpatialExtentType.Region
                        and len(extent.geometries) <= 0
                    ):
                        raise ValueError("Region type requires geometries")
                    if extent.geometries:
                        for geometry_name in extent.geometries:
                            geometry = self.geometry_service.get_geometry_by_name(
                                geometry_name
                            )
                            if geometry:
                                geometries.append(geometry)
                            else:
                                raise ValueError("Geometry not found")
                    spa = SpatialExtent(
                        type=extent.type,
                        region=extent.region if extent.region else None,
                        details=extent.details if extent.details else None,
                        spatial_resolution=extent.spatial_resolution,
                        geometries=geometries,
                        created_by=current_user.email,
                    )
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
                        "temporal_extent",
                        "code_examples",
                        "providers",
                        "main_category",
                        "additional_categories",
                        "keywords",
                    }
                ),
            )
            resource.categories = categories
            resource.providers = providers
            resource.license = license
            resource.temporal_extent = temporal_extents
            resource.spatial_extent = spatial_extent_objects
            resource.examples = examples
            resource.code_examples = code_examples
            resource.keywords = keywords
            resource.created_by = current_user.email

            self.session.add(resource)
            self.session.commit()

            return resource
        except Exception as e:
            # Log unexpected errors and raise a 500 error
            logger.error(f"Unexpected error: {e}")
            self.session.rollback()
            raise e

    def update_resource(self, resource_id, update_dict, current_user: User) -> Resource:
        resource = self.get_resource(resource_id)
        if not resource:
            raise ValueError("Resource not found")

        for key, value in update_dict.items():
            if hasattr(resource, key):
                setattr(resource, key, value)

        setattr(resource, "updated_at", datetime.now())
        setattr(resource, "updated_by", current_user.email)

        self.session.commit()
        return resource

    def get_spatial_extent(self, spatial_extent_id) -> SpatialExtent:
        stmt = select(SpatialExtent).where(SpatialExtent.id == spatial_extent_id)
        return self.session.scalars(stmt).unique().one_or_none()

    def update_spatial_extent(
        self,
        resource_id: uuid.UUID,
        updated_spatial_extent: SpatialExtent,
        spatial_extent_id: uuid.UUID,
        current_user: User,
    ) -> SpatialExtent:
        spatial_extent = self.get_spatial_extent(spatial_extent_id)

        updated_spatial_extent.resource_id = resource_id
        updated_spatial_extent.id = spatial_extent_id
        updated_spatial_extent.created_by = spatial_extent.created_by

        resource = self.get_resource(resource_id)
        if not resource:
            raise ValueError(f"Resource with ID: {resource_id} not found")

        if not spatial_extent:
            raise ValueError(f"Spatial extent with ID: {spatial_extent_id} not found")

        for key, value in vars(updated_spatial_extent).items():
            if hasattr(spatial_extent, key):
                setattr(spatial_extent, key, value)

        setattr(spatial_extent, "updated_at", datetime.now())
        setattr(spatial_extent, "updated_by", current_user.email)

        self.session.commit()
        return spatial_extent

    def create_spatial_extent(
        self, resource_id: uuid.UUID, spatial_extent: SpatialExtent, current_user: User
    ) -> SpatialExtent:
        try:
            geometries = []
            resource = self.get_resource(resource_id)
            if not resource:
                raise ValueError(f"Resource with ID: {resource_id} not found")

            if spatial_extent.geometries:
                for geometry_name in spatial_extent.geometries:
                    geometry = self.geometry_service.get_geometry_by_name(geometry_name)
                    if geometry:
                        geometries.append(geometry)
                    else:
                        raise ValueError(f"Geometry {geometry_name} not found")

            spa = SpatialExtent(
                type=spatial_extent.type,
                region=spatial_extent.region,
                details=spatial_extent.details,
                spatial_resolution=spatial_extent.spatial_resolution,
            )

            spa.created_by = current_user.email
            spa.resource_id = resource_id
            spa.geometries = geometries

            self.session.add(spa)
            self.session.commit()
            return spa

        except Exception as e:
            # Log unexpected errors and raise a 500 error
            logger.error(f"Unexpected error: {e}")
            self.session.rollback()
            raise e

    def create_temporal_extent(
        self, resource_id, temporal_extent_data, current_user: User
    ) -> TemporalExtent:
        try:
            temporal_extent = TemporalExtent(
                **temporal_extent_data.model_dump(exclude_none=True)
            )
            temporal_extent.resource_id = resource_id
            temporal_extent.created_by = current_user.email

            resource = self.get_resource(resource_id)
            if not resource:
                raise ValueError(f"Resource with ID: {resource_id} not found")
            if not temporal_extent:
                raise ValueError("Temporal extent data is required")

            self.session.add(temporal_extent)
            self.session.commit()
            return temporal_extent

        except Exception as e:
            # Log unexpected errors and raise a 500 error
            logger.error(f"Unexpected error: {e}")
            self.session.rollback()
            raise e
