import logging
import uuid

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.models import SpatialExtent, Resource
from data_catalog_backend.dependencies import get_license_service, get_resource_service, get_examples_service
from data_catalog_backend.schemas.resources import ResourcesResponse, ResourceSummeryResponse, ResourceRequest, \
    ResourcesRequest
from data_catalog_backend.services.license_service import LicenseService
from data_catalog_backend.services.resource_service import  ResourceService
from data_catalog_backend.services.examples_service import ExamplesService

router = APIRouter()

@router.post(
    "/resource",
    summary="Add a resource to the database",
    tags=["admin"],
    response_model=ResourcesResponse)

async def post_resource(
    resource_req: ResourceRequest,
    resource_service: ResourceService = Depends(get_resource_service),
    license_service: LicenseService = Depends(get_license_service),
        example_service: ExamplesService = Depends(get_examples_service),
    ) -> ResourcesResponse:

    license = license_service.create_license(resource_req.license)
    examples = example_service.create_examples(resource_req.examples)
    code_examples = example_service.create_code_examples(resource_req.code_examples)

    if not license:
        raise HTTPException(status_code=404, detail="License not found")

    spatial_extent_objects = []

    for extent in resource_req.spatial_extent:
        spa = SpatialExtent(
              type=extent.type,
              region=extent.region if extent.region else None,
              details=extent.details if extent.details else None,
              spatial_resolution=extent.spatial_resolution
        )
        spa.geom = extent.geometry
        spatial_extent_objects.append(spa)

    ed = Resource(
        title=resource_req.title,
        abstract=resource_req.abstract,
        html_content=resource_req.html_content,
        resource_url=resource_req.resource_url,
        documentation_url=resource_req.documentation_url,
        git_url=resource_req.git_url,
        maintenance_and_update_frequency=resource_req.maintenance_and_update_frequency,
        release_date=resource_req.release_date,
        contact=resource_req.contact,
        keywords=resource_req.keywords,
        version=resource_req.version,
        type=resource_req.type,
        spatial_extent=spatial_extent_objects,
        code_examples=code_examples,
        license=license,
        examples=examples
    )

    try:
        created = resource_service.create_resource(ed)

        for extent in created.spatial_extent:
              extent.geometry = extent.geom  # Convert WKB to GeoJSON

        converted = ResourcesResponse.model_validate(created)
        return converted
    except Exception as e:
        logging.error(e)
    raise HTTPException(status_code=500, detail="Unknown error")

@router.post("/resources",
            summary="Get all resources",
            description="Returns all locations from the metadata store",
            tags=["admin"],
            response_model=List[ResourcesResponse],
            response_model_exclude_none=True)
async def get_resources(
        resources_req: ResourcesRequest,
        service: ResourceService = Depends(get_resource_service)
    ) -> List[ResourcesResponse]:
    logging.info('Getting resources')
    resources = service.get_resources(resources_req)
    for resource in resources:
        for extent in resource.spatial_extent:
            extent.geometry = extent.geom  # Convert WKB to GeoJSON
    return resources

@router.get("/resources/summery",
            summary="Get all resource summerys",
            description="Returns all locations from the metadata store",
            tags=["admin"],
            response_model=List[ResourceSummeryResponse],
            response_model_exclude_none=True)
async def get_resource_summeries(service: ResourceService = 
                                Depends(get_resource_service)) -> List[ResourceSummeryResponse]:
      logging.info('getting resource summeries')
      summeries = service.get_resource_summary_list()
      return [ResourceSummeryResponse(**summery) for summery in summeries]

@router.get("/resources/{resource_id}",
            description="Returns one specific resource from the metadata store",
            tags=["admin"],
            response_model=ResourcesResponse,
            response_model_exclude_none=True)
async def get_resource(resource_id: uuid.UUID, 
                       service: ResourceService = Depends(get_resource_service)) -> ResourcesResponse:
        logging.info('getting resource')
        return service.get_resource(resource_id)
