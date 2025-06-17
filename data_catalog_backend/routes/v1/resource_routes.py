import logging
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query

from data_catalog_backend.dependencies import get_resource_service
from data_catalog_backend.routes.admin.authentication import dummy_user
from data_catalog_backend.schemas.User import User
from data_catalog_backend.models import ResourceType, SpatialExtent, SpatialExtentType
from data_catalog_backend.schemas.category import UpdateCategoryRequest
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
from data_catalog_backend.models import (
    ResourceType,
    SpatialExtent,
    SpatialExtentRequestType,
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
        converted = SpatialExtentResponse.model_validate(spatial_extent)
        if not spatial_extent:
            raise HTTPException(status_code=404, detail="Spatial extent not found")
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
