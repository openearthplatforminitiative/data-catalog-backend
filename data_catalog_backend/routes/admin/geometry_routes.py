import logging
from typing import List, Annotated
import uuid
from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import get_geometry_service
from data_catalog_backend.models import Geometry
from data_catalog_backend.routes.admin.authentication import authenticate_user
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.geometry import (
    GeometryResponse,
    GeometryRequest,
    UpdateGeometryRequest,
)
from data_catalog_backend.services.geometry_service import GeometryService

router = APIRouter(prefix="/geometries")
logger = logging.getLogger(__name__)


@router.get(
    "/",
    summary="Get all geometries",
    description="Returns all geometries in our system",
    response_model=List[GeometryResponse],
    response_model_exclude_none=True,
    tags=["geometries"],
)
async def get_geometries(
    geometry_service: GeometryService = Depends(get_geometry_service),
) -> List[GeometryResponse]:
    try:
        logging.info("Fetching all geometries")
        geometries = geometry_service.get_geometries()
        converted = [
            GeometryResponse.model_validate(geometry) for geometry in geometries
        ]
        return converted
    except Exception as e:
        logger.error(f"Error fetching geometries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{geometry_id}",
    description="Returns specific geometry",
    response_model=GeometryResponse,
    response_model_exclude_none=True,
    tags=["geometries"],
)
async def get_geometry(
    geometry_id: uuid.UUID,
    geometry_service: GeometryService = Depends(get_geometry_service),
) -> GeometryResponse:
    try:
        geometry = geometry_service.get_geometry(geometry_id)
        if not geometry:
            raise ValueError(f"Geometry with ID: {geometry_id} not found")
        converted = GeometryResponse.model_validate(geometry)
        return converted
    except ValueError as e:
        logger.warning(f"Value error while fetching geometry: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting geometry {geometry_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/",
    status_code=201,
    summary="Add a geometry",
    tags=["geometries"],
    response_model=GeometryResponse,
)
async def add_geometry(
    geometry_req: GeometryRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    geometry_service: GeometryService = Depends(get_geometry_service),
) -> GeometryResponse:
    try:
        logger.info(f"User {current_user.preferred_username} is adding a geometry")
        geometry = Geometry(**geometry_req.model_dump())

        created = geometry_service.create_geometry(geometry, current_user)

        converted = GeometryResponse.model_validate(created)
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail=f"Error creating geometry: {str(e)}"
        )


@router.put(
    "/{geometry_id}",
    status_code=200,
    description="Update a geometry",
    response_model_exclude_none=True,
    tags=["geometries"],
    response_model=GeometryResponse,
)
async def update_geometry(
    geometry_id: uuid.UUID,
    update_geometry_req: UpdateGeometryRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    geometry_service: GeometryService = Depends(get_geometry_service),
) -> GeometryResponse:
    try:
        geometry_data = update_geometry_req.model_dump(exclude_unset=True)
        geometry = Geometry(**geometry_data)

        updated_geometry = geometry_service.update_geometry(
            geometry_id, geometry, current_user
        )
        return GeometryResponse.model_validate(updated_geometry)
    except Exception as e:
        logger.error(f"Error updating geometry with ID: {geometry_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))
