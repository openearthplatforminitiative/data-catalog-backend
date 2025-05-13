import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response

from data_catalog_backend.dependencies import get_category_service, get_provider_service
from data_catalog_backend.dependencies import get_license_service
from data_catalog_backend.dependencies import (
    get_resource_service,
    get_resource_relation_service,
)
from data_catalog_backend.models import Provider
from data_catalog_backend.schemas.category import CategoryResponse, CategoryRequest
from data_catalog_backend.schemas.license import LicenseResponse, LicenseRequest
from data_catalog_backend.schemas.provider import ProviderRequest, ProviderResponse
from data_catalog_backend.schemas.resource import (
    ResourceRequest,
    ResourceResponse,
    ResourceRelationRequest,
    ResourceRelationResponse,
)
from data_catalog_backend.services.category_service import CategoryService
from data_catalog_backend.services.license_service import LicenseService
from data_catalog_backend.services.provider_service import ProviderService
from data_catalog_backend.services.resource_relation_service import (
    ResourceRelationService,
)
from data_catalog_backend.services.resource_service import ResourceService

router = APIRouter(prefix="/admin")
logger = logging.getLogger(__name__)


@router.get("/test", tags=["admin"], include_in_schema=False)
async def test_admin():
    return Response(content="Test admin successful!", status_code=200)


@router.post(
    "/category",
    summary="Add a category to the database",
    tags=["admin"],
    response_model=CategoryResponse,
    include_in_schema=False,
)
async def add_category(
    category_req: CategoryRequest,
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    try:
        created = category_service.create_category(category_req)
        converted = CategoryResponse.model_validate(created)
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/license",
    summary="Add a license to the database",
    tags=["admin"],
    response_model=LicenseResponse,
    include_in_schema=False,
)
async def add_license(
    license_req: LicenseRequest,
    license_service: LicenseService = Depends(get_license_service),
) -> LicenseResponse:
    try:
        created = license_service.create_license(license_req)
        converted = LicenseResponse.model_validate(created)
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/provider",
    summary="Add a provider to the database",
    tags=["admin"],
    response_model=ProviderResponse,
    include_in_schema=False,
)
async def add_provider(
    provider_req: ProviderRequest,
    service: ProviderService = Depends(get_provider_service),
) -> ProviderResponse:
    try:
        created = service.create_provider(Provider(**provider_req.model_dump()))
        converted = ProviderResponse.model_validate(created)
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/providers/{id}",
    summary="Update a provider",
    description="Updates a provider in the database",
    tags=["admin"],
    response_model=ProviderResponse,
    include_in_schema=False,
)
async def update_provider(
    id: uuid.UUID,
    provider_req: ProviderRequest,
    service: ProviderService = Depends(get_provider_service),
) -> ProviderResponse:
    logger.info("updating provider")
    return service.update_provider(id, provider_req)


@router.post(
    "/resources",
    summary="Add a resource to the database",
    tags=["admin"],
    response_model=ResourceResponse,
    include_in_schema=False,
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
        logger.error(e)
        raise HTTPException(
            status_code=500, detail=f"Error creating resource: {str(e)}"
        )


@router.post(
    "/resources/relations",
    summary="Add a resource relation to the database",
    tags=["admin"],
    response_model=ResourceRelationResponse,
    include_in_schema=False,
)
async def add_resource_relation(
    resource_relation_req: ResourceRelationRequest,
    resource_relation_service: ResourceRelationService = Depends(
        get_resource_relation_service
    ),
) -> ResourceRelationResponse:
    try:
        created = resource_relation_service.create_resource_relation(
            resource_relation_req
        )

        converted = ResourceRelationResponse.model_validate(created)
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail=f"Error creating resource: {str(e)}"
        )
