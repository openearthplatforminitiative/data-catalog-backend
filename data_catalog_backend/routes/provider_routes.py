import logging
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import get_provider_service
from data_catalog_backend.models.resource import Provider
from data_catalog_backend.schemas.provider import ProviderRequest, ProviderResponse
from data_catalog_backend.services.provider_service import ProviderService


router = APIRouter()


@router.post("/provider",
             summary="Add a provider to the database",
             tags=["admin"],
             response_model=ProviderResponse)
async def post_provider(provider_req: ProviderRequest,
                        service: ProviderService = Depends(get_provider_service)
                        ) -> ProviderResponse:
       
      resources = [
            service.get_resource_summery_on_id(resource.resource_id)
            for resource in provider_req.resources
      ]
      resources = [item for sublist in resources for item in sublist]

      ed = Provider(
            name = provider_req.name,
            provider_url = provider_req.provider_url,
            description = provider_req.description,
            resources = resources
      )
      
      try: 
            created = service.create_provider(ed)
            converted = ProviderResponse.model_validate(created)
            return converted
      except Exception as e: 
            logging.error(e)
            raise HTTPException(status_code=500, detail="Unknwon error")

@router.get("/providers",
            summary="Get all providers", 
            description="Returns all providers in our system",
            tags=["admin"],
            response_model=List[ProviderResponse],
            response_model_exclude_none=True)
async def get_providers(service: ProviderService = Depends(get_provider_service)) -> List[ProviderResponse]:
      logging.info('Getting providers')
      return service.get_providers()

@router.get("/providers/{provider_id}",
            description="Returns specific provider",
            tags=["admin"],
            response_model=ProviderResponse,
            response_model_exclude_none=True)
async def get_provider(provider_id: uuid.UUID,
                       service: ProviderService = Depends(get_provider_service)) -> ProviderResponse:
      logging.info('getting provider')
      return service.get_provider(provider_id)