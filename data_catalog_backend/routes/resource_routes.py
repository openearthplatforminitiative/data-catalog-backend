import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import get_resource_service
from data_catalog_backend.schemas.resource import ResourceRequest, ResourceResponse
from data_catalog_backend.schemas.resource_query import (
    ResourceQueryRequest,
    ResourceQueryResponse,
)
from data_catalog_backend.services.resource_service import ResourceService

router = APIRouter()


@router.post(
    "/resources",
    summary="Add a resource to the database",
    tags=["admin"],
    response_model=ResourceResponse,
)
async def add_resource(
    resource_req: ResourceRequest,
    resource_service: ResourceService = Depends(get_resource_service),
) -> ResourceResponse:
    try:
        validated_request = ResourceRequest.model_validate(resource_req)
        created = resource_service.create_resource(validated_request)

        if created.spatial_extent is not None:
            for extent in created.spatial_extent:
                extent.geometry = extent.geom

        converted = ResourceResponse.model_validate(created)
        return converted
    except Exception as e:
        logging.error(e)
        raise HTTPException(
            status_code=500, detail=f"Error creating resource: {str(e)}"
        )


@router.get(
    "/resources",
    summary="Get all resources",
    description="Returns all locations from the metadata store",
    response_model=ResourceQueryResponse,
    response_model_exclude_none=True,
)
async def get_resources(
    resources_req: ResourceQueryRequest,
    page: int = 0,
    per_page: int = 10,
    service: ResourceService = Depends(get_resource_service),
) -> ResourceQueryResponse:
    logging.info("Getting resources with non-geospatial filters")
    logging.info(resources_req)
    resources_req.features = None
    resources_req.spatial = None
    resources = service.get_resources(page, per_page, resources_req)
    return resources


@router.post(
    "/resources/search",
    summary="Search resources with all filters, including geospatial",
    description="Search resources using all available filters, including geospatial filters.",
    response_model=ResourceQueryResponse,
    response_model_exclude_none=True,
)
async def search_resources(
    resources_req: ResourceQueryRequest,
    page: int = 0,
    per_page: int = 10,
    service: ResourceService = Depends(get_resource_service),
) -> ResourceQueryResponse:
    logging.info("Searching resources with all filters")
    logging.info(resources_req)
    resources = service.get_resources(page, per_page, resources_req)
    return resources


@router.get(
    "/resources/{resource_id}",
    description="Returns one specific resource from the metadata store",
    response_model=ResourceResponse,
    response_model_exclude_none=True,
)
async def get_resource(
    resource_id: uuid.UUID, service: ResourceService = Depends(get_resource_service)
) -> ResourceResponse:
    resource = service.get_resource(resource_id)
    try:
        for extent in resource.spatial_extent:
            extent.geometry = extent.geom  # Convert WKB to GeoJSON

        converted = ResourceResponse.model_validate(resource)
        return converted
    except Exception as e:
        logging.error(e)
    raise HTTPException(status_code=500, detail="Unknown error")
