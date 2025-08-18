import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import (
    get_resource_relation_service,
)
from data_catalog_backend.routes.admin.authentication import authenticate_user
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.resource import (
    ResourceRelationRequest,
    ResourceRelationResponse,
)
from data_catalog_backend.services.resource_relation_service import (
    ResourceRelationService,
)

router = APIRouter(prefix="/resourcerelations")
logger = logging.getLogger(__name__)


@router.post(
    "/",
    summary="Add a resource relation to the database",
    tags=["resource_relations"],
    response_model=ResourceRelationResponse,
)
async def add_resource_relation(
    resource_relation_req: ResourceRelationRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    resource_relation_service: ResourceRelationService = Depends(
        get_resource_relation_service
    ),
) -> ResourceRelationResponse:
    try:
        logger.info(
            f"User {current_user.preferred_username} is adding a resource relation"
        )
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
