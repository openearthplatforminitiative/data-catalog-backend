import logging
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import get_provider_service
from data_catalog_backend.schemas.provider import ProviderResponse
from data_catalog_backend.services.provider_service import ProviderService

router = APIRouter(prefix="/providers")
logger = logging.getLogger(__name__)


@router.get(
    "/",
    summary="Get all providers",
    description="Returns all providers in our system",
    response_model=List[ProviderResponse],
    response_model_exclude_none=True,
    tags=["providers"],
)
async def get_providers(
    provider_service: ProviderService = Depends(get_provider_service),
) -> List[ProviderResponse]:
    try:
        logging.info("Fetching all providers")
        providers = provider_service.get_providers()
        converted = [
            ProviderResponse.model_validate(provider) for provider in providers
        ]
        return converted
    except Exception as e:
        logger.error(f"Error fetching providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{provider_id}",
    description="Returns specific provider",
    response_model=ProviderResponse,
    response_model_exclude_none=True,
    tags=["providers"],
)
async def get_provider(
    provider_id: uuid.UUID,
        provider_service: ProviderService = Depends(get_provider_service)
) -> ProviderResponse:
    try:
        provider = provider_service.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Provider with ID: {provider_id} not found")
        converted = ProviderResponse.model_validate(provider)
        return converted
    except ValueError as e:
        logger.warning(f"Value error while fetching provider: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
