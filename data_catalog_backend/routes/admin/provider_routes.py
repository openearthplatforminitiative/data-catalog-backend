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
    status_code=201,
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
        provider_data = provider_req.model_dump()
        provider = Provider(**provider_data)
        created_provider = service.create_provider(provider, current_user)
        converted = ProviderResponse.model_validate(created_provider)
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{provider_id}",
    status_code=200,
    summary="Update a provider",
    description="Updates a provider in the database",
    tags=["admin"],
    response_model=ProviderResponse,
)
async def update_provider(
    provider_id: uuid.UUID,
    provider_req: ProviderRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    provider_service: ProviderService = Depends(get_provider_service),
) -> ProviderResponse:
    try:
        logger.info(f"User {current_user.preferred_username} is updating a provider")
        provider_data = provider_req.model_dump()
        provider = Provider(**provider_data)
        updated_provider = provider_service.update_provider(
            provider_id, provider, current_user
        )
        converted = ProviderResponse.model_validate(updated_provider)
        return converted
    except ValueError as e:
        logger.error(f"Value error while updating category: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error while updating provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{provider_id}",
    status_code=204,
    description="Delete a provider",
    response_model_exclude_none=True,
    tags=["admin"],
)
async def delete_provider(
    provider_id: uuid.UUID,
    provider_service: ProviderService = Depends(get_provider_service),
):
    try:
        logging.info(f"Deleting provider with id {provider_id}")
        provider_service.delete_provider(provider_id)
    except ValueError as ve:
        logger.warning(
            f"Validation error while deleting provider with ID: {provider_id} - {str(ve)}"
        )
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error deleting provider with id {provider_id} - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
