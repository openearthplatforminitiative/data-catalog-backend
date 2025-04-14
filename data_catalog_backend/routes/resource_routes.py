import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import get_resource_service
from data_catalog_backend.schemas.resource import ResourceRequest, ResourceResponse
from data_catalog_backend.schemas.resource_query import ResourceQueryRequest, ResourceQueryResponse
from data_catalog_backend.services.resource_service import  ResourceService

router = APIRouter()

@router.post(
    "/resource",
    summary="Add a resource to the database",
    tags=["admin"],
    response_model=ResourceRequest)
async def post_resource(
        resource_req: ResourceRequest,
        resource_service: ResourceService = Depends(get_resource_service),
    ) -> ResourceResponse:
    try:
        created = resource_service.create_resource(resource_req)

        for extent in created.spatial_extent:
              extent.geometry = extent.geom  # Convert WKB to GeoJSON

        converted = ResourceResponse.model_validate(created)
        return converted
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=e)

@router.post("/resources",
            summary="Get all resources",
            description="Returns all locations from the metadata store",
            tags=["admin"],
            response_model=ResourceQueryResponse,
            response_model_exclude_none=True)
async def get_resources(
        resources_req: ResourceQueryRequest,
        page: int = 0,
        per_page: int = 10,
        service: ResourceService = Depends(get_resource_service)
    ) -> ResourceQueryResponse:
    logging.info('Getting resources')
    logging.info(resources_req)
    resources = service.get_resources(page, per_page, resources_req)
    return resources

@router.get("/resources/{resource_id}",
            description="Returns one specific resource from the metadata store",
            tags=["admin"],
            response_model=ResourceResponse,
            response_model_exclude_none=True)
async def get_resource(resource_id: uuid.UUID, service: ResourceService = Depends(get_resource_service)) -> ResourceResponse:
        resource = service.get_resource(resource_id)
        try:
            for extent in resource.spatial_extent:
                extent.geometry = extent.geom  # Convert WKB to GeoJSON

            converted = ResourceResponse.model_validate(resource)
            return converted
        except Exception as e:
            logging.error(e)
        raise HTTPException(status_code=500, detail="Unknown error")