import logging
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import get_provider_service
from data_catalog_backend.models import Provider
from data_catalog_backend.schemas.provider import ProviderRequest, ProviderResponse
from data_catalog_backend.services.provider_service import ProviderService


router = APIRouter()


@router.get(
    "/providers",
    summary="Get all providers",
    description="Returns all providers in our system",
    response_model=List[ProviderResponse],
    response_model_exclude_none=True,
    tags=["providers"],
)
async def get_providers(
    service: ProviderService = Depends(get_provider_service),
) -> List[ProviderResponse]:
    return service.get_providers()


@router.get(
    "/providers/{id}",
    description="Returns specific provider",
    response_model=ProviderResponse,
    response_model_exclude_none=True,
    tags=["providers"],
)
async def get_provider(
    id: uuid.UUID, service: ProviderService = Depends(get_provider_service)
) -> ProviderResponse:
    return service.get_provider(id)
