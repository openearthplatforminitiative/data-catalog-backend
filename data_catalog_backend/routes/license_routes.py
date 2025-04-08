import logging
from http.client import HTTPException

from fastapi import APIRouter, Depends

from data_catalog_backend.dependencies import get_license_service
from data_catalog_backend.schemas.license import LicenseResponse, LicenseRequest
from data_catalog_backend.services.license_service import LicenseService

router = APIRouter()

@router.post(
    "/license",
    summary="Add a license to the database",
    tags=["admin"],
    response_model=LicenseResponse)
async def post_license(
        license_req: LicenseRequest,
        license_service: LicenseService = Depends(get_license_service),
) -> LicenseResponse:
    try:
        created = license_service.create_license(license_req)
        converted = LicenseResponse.model_validate(created)
        return converted
    except Exception as e:
        logging.error(e)
    raise HTTPException(status_code=500, detail="Unknown error")