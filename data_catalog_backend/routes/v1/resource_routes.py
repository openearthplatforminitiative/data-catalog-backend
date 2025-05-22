import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import get_resource_service
from data_catalog_backend.models import SpatialExtent, SpatialExtentType
from data_catalog_backend.schemas.category import UpdateCategoryRequest
from data_catalog_backend.schemas.code import (
    UpdateCodeExampleRequest,
    UpdateCodeRequest,
)
from data_catalog_backend.schemas.resource import (
    ResourceResponse,
    UpdateResourceRequest,
)
from data_catalog_backend.schemas.resource_query import (
    ResourceQueryRequest,
    ResourceQueryResponse,
)
from data_catalog_backend.schemas.spatial_extent import (
    SpatialExtentRequest,
    UpdateSpatialExtentRequest,
    SpatialExtentResponse,
)
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
    resources_req: ResourceQueryRequest,
    page: int = 0,
    per_page: int = 10,
    service: ResourceService = Depends(get_resource_service),
) -> ResourceQueryResponse:
    logger.info("Getting resources with non-geospatial filters")
    logger.info(resources_req)
    resources_req.features = None
    resources_req.spatial = None
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
    print("getting resource", resource_id)
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
    "/resources/{resource_id}",
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
        print("Resource not found hello hello")
        raise HTTPException(status_code=404, detail="Resource not found")

    try:
        update_dict = update_data.model_dump(exclude_unset=True)
        """
        if "spatial_extent" in update_dict:
            spatial_extent_data = update_dict.pop("spatial_extent")
            validated_spatial_extent = []

            for extent in spatial_extent_data:
                validated_extent = UpdateSpatialExtentRequest(**extent)
                extent_data = validated_extent.model_dump()

                extent_data["resource_id"] = resource_id
                print(extent_data.keys())

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
        """
        updated_resource = service.update_resource(resource_id, update_dict)

        return ResourceResponse.model_validate(updated_resource)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/resources/{resource_id}/spatial_extent",
    description="Adds spatial extent data to the resource",
    response_model=SpatialExtentResponse,
    response_model_exclude_none=True,
    tags=["resources"],
)
async def add_spatial_extent(
    resource_id: uuid.UUID,
    spatial_extent_data: SpatialExtentRequest,
    service: ResourceService = Depends(get_resource_service),
) -> SpatialExtentResponse:
    try:
        validated_spatial_extent = SpatialExtentRequest(**spatial_extent_data)
        extent_data = validated_spatial_extent.model_dump()
        extent_data["resource_id"] = resource_id
        spatial_extent_instance = service.create_spatial_extent(extent_data)
        return SpatialExtentResponse.model_validate(spatial_extent_instance)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/resources/{resource_id}/{spatial_extent_id",
    description="Update a spatial extent in a resource",
    response_model=SpatialExtentResponse,
    response_model_exclude_none=True,
    tags=["resources"],
)
async def update_spatial_extent(
    resource_id: uuid.UUID,
    spatial_extent_id: uuid.UUID,
    spatial_extent_data: UpdateSpatialExtentRequest,
    service: ResourceService = Depends(get_resource_service),
) -> SpatialExtentResponse:
    try:
        validated_spatial_extent = UpdateSpatialExtentRequest(**spatial_extent_data)
        extent_data = validated_spatial_extent.model_dump()
        extent_data["resource_id"] = resource_id
        spatial_extent_instance = service.update_spatial_extent(
            resource_id, spatial_extent_id, extent_data
        )
        return SpatialExtentResponse.model_validate(spatial_extent_instance)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
