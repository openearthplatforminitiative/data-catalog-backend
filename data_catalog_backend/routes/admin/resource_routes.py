import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import (
    get_resource_service,
)
from data_catalog_backend.routes.admin.authentication import authenticate_user
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.resource import (
    ResourceRequest,
    ResourceResponse,
)
from data_catalog_backend.services.resource_service import ResourceService

router = APIRouter(prefix="/resources")
logger = logging.getLogger(__name__)


@router.post(
    "/",
    summary="Add a resource to the database",
    tags=["admin"],
    response_model=ResourceResponse,
)
async def add_resource(
    resource_req: ResourceRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    resource_service: ResourceService = Depends(get_resource_service),
) -> ResourceResponse:
    try:
        logger.info(f"User {current_user.preferred_username} is adding a resource")
        validated_request = ResourceRequest.model_validate(resource_req)
        created = resource_service.create_resource(validated_request, current_user)

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


@router.delete(
    "/{resource_id}",
    status_code=204,
    description="Delete a resource from the metadata store",
    tags=["admin"],
    response_model=ResourceResponse,
    response_model_exclude_none=True,
)
async def delete_resource(
    resource_id: uuid.UUID,
    current_user: Annotated[User, Depends(authenticate_user)],
    service: ResourceService = Depends(get_resource_service),
):
    try:
        logging.info(f"Deleting resource with id {resource_id}")
        service.delete_resource(resource_id, current_user)
    except Exception as e:
        logger.error(f"Error deleting resource: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    return
