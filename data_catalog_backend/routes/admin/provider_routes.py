import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import get_provider_service
from data_catalog_backend.models import Provider
from data_catalog_backend.routes.admin.authentication import authenticate_user
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.provider import ProviderRequest, ProviderResponse
from data_catalog_backend.services.provider_service import ProviderService

router = APIRouter(prefix="/providers")
logger = logging.getLogger(__name__)


@router.post(
    "/",
    summary="Add a provider to the database",
    tags=["admin"],
    response_model=ProviderResponse,
)
async def add_provider(
    provider_req: ProviderRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    service: ProviderService = Depends(get_provider_service),
) -> ProviderResponse:
    try:
        logger.info(f"User {current_user.preferred_username} is adding a provider")
        created = service.create_provider(Provider(**provider_req.model_dump()))
        converted = ProviderResponse.model_validate(created)
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{id}",
    summary="Update a provider",
    description="Updates a provider in the database",
    tags=["admin"],
    response_model=ProviderResponse,
)
async def update_provider(
    id: uuid.UUID,
    provider_req: ProviderRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    service: ProviderService = Depends(get_provider_service),
) -> ProviderResponse:
    logger.info(f"User {current_user.preferred_username} is updating a provider")
    return service.update_provider(id, provider_req)
