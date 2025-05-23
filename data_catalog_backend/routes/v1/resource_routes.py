import logging
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query

from data_catalog_backend.dependencies import get_resource_service
from data_catalog_backend.routes.admin.authentication import dummy_user
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.code import (
    CodeExampleResponse,
    CodeExampleRequest,
    UpdateCodeExampleRequest,
)
from data_catalog_backend.schemas.example import (
    ExampleRequest,
    ExampleResponse,
    UpdateExampleRequest,
)
from data_catalog_backend.schemas.resource import (
    ResourceResponse,
    UpdateResourceRequest,
)
from data_catalog_backend.models import ResourceType, SpatialExtent, SpatialExtentRequestType
from data_catalog_backend.schemas.resource import (
    ResourceResponse,
    UpdateResourceRequest,
)
from data_catalog_backend.schemas.resource_query import (
    ResourceQueryRequest,
    ResourceQueryResponse,
)
from data_catalog_backend.schemas.spatial_extent import (
    SpatialExtentResponse,
    SpatialExtentRequest,
    UpdateSpatialExtentRequest,
)
from data_catalog_backend.schemas.temporal_extent import TemporalExtentResponse
from data_catalog_backend.services.resource_service import ResourceService

router = APIRouter(prefix="/resources")
logger = logging.getLogger(__name__)


@router.get(
    "/",
    summary="Get all resources",
    description="Returns all locations from the metadata store",
    response_model=ResourceQueryResponse,
    response_model_exclude_none=True,
    tags=["resources"],
)
async def get_resources(
    types: Optional[List[ResourceType]] = Query(
        None, description="Filter by resource types"
    ),
    spatial: Optional[List[SpatialExtentRequestType]] = Query(
        None, description="Filter by spatial extent types"
    ),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    years: Optional[List[str]] = Query(None, description="Filter by years"),
    page: int = Query(0, description="Page number for pagination"),
    per_page: int = Query(10, description="Number of items per page"),
    service: ResourceService = Depends(get_resource_service),
) -> ResourceQueryResponse:
    resources_req = ResourceQueryRequest(
        types=types,
        spatial=spatial,
        categories=None,
        providers=None,
        tags=tags,
        years=years,
        features=None,  # Explicitly set to None for GET endpoint
    )

    logger.info("Getting resources with non-geospatial filters")
    logger.info(resources_req)
    resources = service.get_resources(page, per_page, resources_req)
    return resources


@router.post(
    "/search",
    summary="Search resources with all filters, including geospatial",
    description="Search resources using all available filters, including geospatial filters.",
    response_model=ResourceQueryResponse,
    response_model_exclude_none=True,
    tags=["resources"],
)
async def search_resources(
    resources_req: ResourceQueryRequest,
    page: int = 0,
    per_page: int = 10,
    service: ResourceService = Depends(get_resource_service),
) -> ResourceQueryResponse:
    logger.info("Searching resources with all filters")
    logger.info(resources_req)
    resources = service.get_resources(page, per_page, resources_req)
    return resources


@router.get(
    "/{resource_id}",
    description="Returns one specific resource from the metadata store",
    response_model=ResourceResponse,
    response_model_exclude_none=True,
    tags=["resources"],
)
async def get_resource(
    resource_id: uuid.UUID, service: ResourceService = Depends(get_resource_service)
) -> ResourceResponse:
    resource = service.get_resource(resource_id)
    try:
        for extent in resource.spatial_extent:
            extent.geometry = extent.geom  # Convert WKB to GeoJSON

        converted = ResourceResponse.model_validate(resource)
        logger.info(converted)
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{resource_id}",
    description="Update a resource",
    response_model=ResourceResponse,
    response_model_exclude_none=True,
    tags=["resources"],
)
async def update_resource(
    resource_id: uuid.UUID,
    update_data: UpdateResourceRequest,
    service: ResourceService = Depends(get_resource_service),
) -> ResourceResponse:
    resource = service.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    try:
        update_dict = update_data.model_dump(exclude_unset=True)
        if "spatial_extent" in update_dict:
            spatial_extent_data = update_dict.pop("spatial_extent")
            validated_spatial_extent = []

            for extent in spatial_extent_data:
                validated_extent = UpdateSpatialExtentRequest(**extent)
                extent_data = validated_extent.model_dump()

                extent_data["resource_id"] = resource_id

                spatial_extent_instance = service.update_spatial_extent(
                    resource_id, extent_data
                )

                validated_spatial_extent.append(spatial_extent_instance)

            update_dict["spatial_extent"] = validated_spatial_extent

        if "code_examples" in update_dict:
            code_examples = update_dict.pop("code_examples")
            validated_code_examples = []

            for example in code_examples:
                validated_example = UpdateCodeExampleRequest(**example)
                example_data = validated_example.model_dump()

                example_data["resource_id"] = resource_id
                code_example_instance = (
                    service.code_example_service.update_code_example(example_data)
                )

                validated_code_examples.append(code_example_instance)

            print("update_dict[code_examples]", update_dict["code_examples"])
            update_dict["code_examples"] = validated_code_examples
        print(update_dict.keys())
        print(update_dict.values())
        # main_category or additional_categories
        if "categories" in update_dict:
            categories = update_dict.pop("categories")
            validated_categories = []
            print("update_dict[categories]", update_dict["categories"])
            for category in categories:
                validated_category = UpdateCategoryRequest(**category)
                category_data = validated_category.model_dump()
                print("category_dATA: ", category_data)
                category_data["resource_id"] = resource_id
                category_instance = service.category_service.update_category(
                    category_data
                )

                validated_categories.append(category_instance)

            update_dict["categories"] = validated_categories

        updated_resource = service.update_resource(resource_id, update_dict)

        return ResourceResponse.model_validate(updated_resource)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/spatial_extent/{spatial_extent_id}",
    description="Get spatial extent from metadata store",
    response_model=SpatialExtentResponse,
    response_model_exclude_none=True,
    tags=["resources"],
)
async def get_spatial_extent(
    spatial_extent_id: uuid.UUID,
    service: ResourceService = Depends(get_resource_service),
) -> SpatialExtentResponse:
    try:
        spatial_extent = service.get_spatial_extent(spatial_extent_id)
        if not spatial_extent:
            raise HTTPException(status_code=404, detail="Spatial extent not found")
        return spatial_extent
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{resource_id}/spatial_extent",
    description="Add a spatial extent to a resource",
    response_model=SpatialExtentResponse,
    response_model_exclude_none=True,
    tags=["resources"],
)
async def add_spatial_extent(
    resource_id: uuid.UUID,
    spatial_extent: SpatialExtentRequest,
    service: ResourceService = Depends(get_resource_service),
) -> None:
    try:
        created_spatial_extent = service.create_spatial_extent(
            resource_id, spatial_extent, user=dummy_user
        )
        return created_spatial_extent
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{resource_id}/spatial_extent/{spatial_extent_id}",
    description="Update a spatial extent of a resource",
    response_model=SpatialExtentResponse,
    response_model_exclude_none=True,
    tags=["resources"],
)
async def update_spatial_extent(
    resource_id: uuid.UUID,
    spatial_extent: UpdateSpatialExtentRequest,
    spatial_extent_id: uuid.UUID,
    service: ResourceService = Depends(get_resource_service),
) -> None:
    try:
        updated_spatial_extent = service.update_spatial_extent(
            resource_id, spatial_extent, spatial_extent_id
        )
        return updated_spatial_extent
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{resource_id}/code_examples",
    description="Add code examples to a resource",
    response_model=List[CodeExampleResponse],
    response_model_exclude_none=True,
    tags=["resources"],
)
async def add_code_examples(
    resource_id: uuid.UUID,
    code_examples: List[CodeExampleRequest],
    service: ResourceService = Depends(get_resource_service),
) -> List[CodeExampleResponse]:
    try:
        created_code_examples = service.code_example_service.create_code_examples(
            code_examples, resource_id, user=dummy_user
        )
        return [
            CodeExampleResponse.model_validate(example).model_dump()
            for example in created_code_examples
        ]
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{resource_id}/code_examples/{code_example_id}",
    description="Update a code example of a resource",
    response_model=CodeExampleResponse,
    response_model_exclude_none=True,
    tags=["resources"],
)
async def update_code_example(
    resource_id: uuid.UUID,
    code_example_id: uuid.UUID,
    code_example: UpdateCodeExampleRequest,
    service: ResourceService = Depends(get_resource_service),
) -> CodeExampleResponse:
    try:
        updated_code_example = service.code_example_service.update_code_example(
            resource_id=resource_id,
            code_example_id=code_example_id,
            example_data=code_example,
            user=dummy_user,
        )
        return CodeExampleResponse.model_validate(updated_code_example).model_dump()
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{resource_id}/examples",
    description="Add examples to a resource",
    response_model=List[ExampleResponse],
    response_model_exclude_none=True,
    tags=["resources"],
)
async def add_examples(
    resource_id: uuid.UUID,
    examples: List[ExampleRequest],
    service: ResourceService = Depends(get_resource_service),
) -> List[ExampleResponse]:
    try:

        created_examples = service.example_service.create_examples(
            examples, resource_id, user=dummy_user
        )
        logger.info(f"Response data: {created_examples}")
        return [
            ExampleResponse.model_validate(example).model_dump()
            for example in created_examples
        ]
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{resource_id}/examples/{example_id}",
    description="Update an example of a resource",
    response_model=ExampleResponse,
    response_model_exclude_none=True,
    tags=["resources"],
)
async def update_example(
    example_id: uuid.UUID,
    example: UpdateExampleRequest,
    service: ResourceService = Depends(get_resource_service),
) -> ExampleResponse:
    try:
        updated_example = service.example_service.update_example(
            example_id=example_id, example_data=example
        )
        return ExampleResponse.model_validate(updated_example).model_dump()
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{resource_id}/temporal_extent",
    description="Add a temporal extent to a resource",
    response_model=List[TemporalExtentResponse],
    response_model_exclude_none=True,
    tags=["resources"],
)
async def add_temporal_extent(
    resource_id: uuid.UUID,
    temporal_extent: TemporalExtentResponse,
    service: ResourceService = Depends(get_resource_service),
) -> List[TemporalExtentResponse]:
    try:
        created_temporal_extent = service.create_temporal_extent(
            resource_id, temporal_extent
        )
        return created_temporal_extent
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
