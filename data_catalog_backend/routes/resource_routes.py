import logging
import uuid

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.models import SpatialExtent, Resource
from data_catalog_backend.dependencies import get_license_service, get_resource_service, get_examples_service, \
    get_provider_service, get_category_service
from data_catalog_backend.schemas.resource import ResourcesResponse, ResourceRequest, ResourcesRequest, \
    ResourceResponse
from data_catalog_backend.services.category_service import CategoryService
from data_catalog_backend.services.license_service import LicenseService
from data_catalog_backend.services.provider_service import ProviderService
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
        provider_service: ProviderService = Depends(get_provider_service),
        category_service: CategoryService = Depends(get_category_service)
    ) -> ResourcesResponse:

    license = license_service.create_or_find_license(resource_req.license)

    providers = []
    for provider_req in resource_req.providers:
        provider = provider_service.create_or_find_provider(provider_req)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        providers.append(provider)

    categories = []
    for category in resource_req.categories:
        cat = category_service.create_or_find_category(category)
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        categories.append(cat)

    examples = []
    if resource_req.examples:
        examples = example_service.create_examples(resource_req.examples)

    code_examples = []
    if resource_req.code_examples:
        code_examples = example_service.create_code_examples(resource_req.code_examples)

    if not license:
        raise HTTPException(status_code=404, detail="License not found")

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

    resource_data = resource_req.model_dump()
    resource_data.update({
        "spatial_extent": spatial_extent_objects,
        "categories": categories,
        "code_examples": code_examples,
        "license": license,
        "providers": providers,
        "examples": examples
    })
    resource_obj = Resource(**resource_data)

    try:
        created = resource_service.create_resource(resource_obj)

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
            response_model=ResourcesResponse,
            response_model_exclude_none=True)
async def get_resources(
        resources_req: ResourcesRequest,
        page: int = 0,
        per_page: int = 10,
        service: ResourceService = Depends(get_resource_service)
    ) -> ResourcesResponse:
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
@router.put("/resources/{id}",
            summary="Update a resource",
            description="Updates a resource in the database",
            tags=["admin"],
            response_model=ResourcesResponse)
async def update_resource(id: uuid.UUID,
                           resource_req: ResourceRequest,
                           service: ResourceService = Depends(get_resource_service)) -> ResourcesResponse:
        pass
        # logging.info('updating resource')
        # return service.update_resource(id, resource_req)