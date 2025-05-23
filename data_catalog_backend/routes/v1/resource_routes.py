import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import get_resource_service
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
        print("Resource not found hello hello")
        raise HTTPException(status_code=404, detail="Resource not found")

    try:
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_resource = service.update_resource(resource_id, update_dict)

        return ResourceResponse.model_validate(updated_resource)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{spatial_extent_id}",
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
            resource_id, spatial_extent
        )
        return created_spatial_extent
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{resource_id}/{spatial_extent_id}",
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
