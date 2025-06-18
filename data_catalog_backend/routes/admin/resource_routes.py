import logging
import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import (
    get_resource_service,
)
from data_catalog_backend.models import (
    Category,
    SpatialExtent,
    Resource,
    CodeExamples,
    Examples,
)
from data_catalog_backend.routes.admin.authentication import authenticate_user
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.category import UpdateCategoryRequest
from data_catalog_backend.schemas.code import (
    UpdateCodeExampleRequest,
    CodeExampleResponse,
    CodeExampleRequest,
)
from data_catalog_backend.schemas.example import (
    ExampleResponse,
    UpdateExampleRequest,
    ExampleRequest,
)
from data_catalog_backend.schemas.resource import (
    ResourceRequest,
    ResourceResponse,
    UpdateResourceRequest,
)
from data_catalog_backend.schemas.spatial_extent import (
    UpdateSpatialExtentRequest,
    SpatialExtentResponse,
    SpatialExtentRequest,
)
from data_catalog_backend.schemas.temporal_extent import TemporalExtentResponse
from data_catalog_backend.services.resource_service import ResourceService

router = APIRouter(prefix="/resources")
logger = logging.getLogger(__name__)


@router.post(
    "/",
    status_code=201,
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
        resource_data = resource_req.model_dump()
        resource = Resource(**resource_data)

        created = resource_service.create_resource(resource, current_user)

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


@router.put(
    "/{resource_id}",
    status_code=200,
    description="Update a resource",
    response_model_exclude_none=True,
    tags=["admin"],
    response_model=ResourceResponse,
)
async def update_resource(
    resource_id: uuid.UUID,
    update_resource_req: UpdateResourceRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    resource_service: ResourceService = Depends(get_resource_service),
) -> ResourceResponse:
    resource = resource_service.get_resource(resource_id)
    if not resource:
        raise ValueError("Resource not found")

    try:
        updated_resource = update_resource_req.model_dump(exclude_unset=True)
        if "spatial_extent" in updated_resource:
            spatial_extent_data = updated_resource.pop("spatial_extent")
            validated_spatial_extent = []
            try:
                for extent in spatial_extent_data:
                    validated_extent = UpdateSpatialExtentRequest(**extent)
                    extent_data = validated_extent.model_dump()

                    extent_data["resource_id"] = resource_id
                    updated_spatial_extent = SpatialExtent(**extent_data)

                    spatial_extent_instance = resource_service.update_spatial_extent(
                        resource_id,
                        updated_spatial_extent,
                        updated_spatial_extent.id,
                        current_user,
                    )

                    validated_spatial_extent.append(spatial_extent_instance)

            except ValueError as ve:
                logger.error(f"Validation error for spatial extent: {ve}")
                raise HTTPException(status_code=404, detail=str(ve))
            except Exception as e:
                logger.error(f"Unexpected error while processing spatial extent: {e}")
                raise HTTPException(status_code=500, detail=str(e))

            updated_resource["spatial_extent"] = validated_spatial_extent

            if "code_examples" in updated_resource:
                code_examples = updated_resource.pop("code_examples")
                validated_code_examples = []

                try:
                    for example in code_examples:
                        validated_example = UpdateCodeExampleRequest(**example)
                        example_data = validated_example.model_dump()

                        example_data["resource_id"] = resource_id
                        code_example_instance = (
                            resource_service.code_example_service.update_code_example(
                                resource_id, example_data, example_data.id, current_user
                            )
                        )

                        validated_code_examples.append(code_example_instance)
                except ValueError as ve:
                    logger.error(f"Validation error for code example: {ve}")
                    raise HTTPException(status_code=400, detail=str(ve))
                except Exception as e:
                    logger.error(
                        f"Unexpected error while processing code examples: {e}"
                    )
                    raise HTTPException(status_code=500, detail=str(e))

                updated_resource["code_examples"] = validated_code_examples

        # main_category or additional_categories
        if "categories" in updated_resource:
            categories = updated_resource.pop("categories")
            validated_categories = []
            try:
                for category in categories:
                    validated_category = UpdateCategoryRequest(**category)
                    category_data = validated_category.model_dump()
                    category_data["resource_id"] = resource_id
                    category_instance = Category(**category_data)
                    updated_category = (
                        resource_service.category_service.update_category(
                            category_instance, category.id, current_user
                        )
                    )

                    validated_categories.append(updated_category)
            except ValueError as ve:
                logger.error(f"Validation error for category: {ve}")
                raise HTTPException(status_code=400, detail=str(ve))
            except Exception as e:
                logger.error(f"Unexpected error while processing categories: {e}")
                raise HTTPException(status_code=500, detail=str(e))

            updated_resource["categories"] = validated_categories

        updated_resource = resource_service.update_resource(
            resource_id, updated_resource, current_user
        )

        return ResourceResponse.model_validate(updated_resource)
    except ValueError as e:
        logger.error(f"Value error while updating resource: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating resource with ID: {resource_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{resource_id}/spatial_extent",
    status_code=201,
    description="Add a spatial extent to a resource",
    response_model=SpatialExtentResponse,
    response_model_exclude_none=True,
    tags=["admin"],
)
async def add_spatial_extent(
    resource_id: uuid.UUID,
    spatial_extent_req: SpatialExtentRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    resource_service: ResourceService = Depends(get_resource_service),
) -> SpatialExtentResponse:
    try:
        spatial_extent_data = spatial_extent_req.model_dump()
        spatial_extent = SpatialExtent(**spatial_extent_data)
        created_spatial_extent = resource_service.create_spatial_extent(
            resource_id, spatial_extent, current_user
        )
        converted = SpatialExtentResponse.model_validate(created_spatial_extent)
        return converted
    except ValueError as e:
        logger.error(f"Value error while adding spatial extent: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            f"Error adding spatial extent to resource with ID: {resource_id} - {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{resource_id}/spatial_extent/{spatial_extent_id}",
    status_code=200,
    description="Update a spatial extent of a resource",
    response_model=SpatialExtentResponse,
    response_model_exclude_none=True,
    tags=["admin"],
)
async def update_spatial_extent(
    resource_id: uuid.UUID,
    spatial_extent_req: UpdateSpatialExtentRequest,
    spatial_extent_id: uuid.UUID,
    current_user: Annotated[User, Depends(authenticate_user)],
    resource_service: ResourceService = Depends(get_resource_service),
) -> SpatialExtentResponse:
    try:
        spatial_extent_data = spatial_extent_req.model_dump()
        spatial_extent = SpatialExtent(**spatial_extent_data)
        updated_spatial_extent = resource_service.update_spatial_extent(
            resource_id, spatial_extent, spatial_extent_id, current_user
        )
        converted = SpatialExtentResponse.model_validate(updated_spatial_extent)
        return converted
    except ValueError as e:
        logger.error(f"Value error while updating spatial extent: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while updating spatial extent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{resource_id}/temporal_extent",
    status_code=201,
    description="Add a temporal extent to a resource",
    response_model=List[TemporalExtentResponse],
    response_model_exclude_none=True,
    tags=["admin"],
)
async def add_temporal_extent(
    resource_id: uuid.UUID,
    temporal_extent: TemporalExtentResponse,
    current_user: Annotated[User, Depends(authenticate_user)],
    temporal_extent_service: ResourceService = Depends(get_resource_service),
) -> List[TemporalExtentResponse]:
    try:
        created_temporal_extent = temporal_extent_service.create_temporal_extent(
            resource_id, temporal_extent, current_user
        )
        converted = [TemporalExtentResponse.model_validate(created_temporal_extent)]
        return converted
    except ValueError as e:
        logger.error(f"Value error while adding temporal extent: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{resource_id}/code_examples",
    status_code=201,
    description="Add code examples to a resource",
    response_model=List[CodeExampleResponse],
    response_model_exclude_none=True,
    tags=["admin"],
)
async def add_code_examples(
    resource_id: uuid.UUID,
    code_examples_req: List[CodeExampleRequest],
    current_user: Annotated[User, Depends(authenticate_user)],
    service: ResourceService = Depends(get_resource_service),
) -> List[CodeExampleResponse]:
    try:
        logger.info(f"Adding code examples for resource {resource_id}")
        code_examples_data = code_examples_req.model_dump()
        code_examples = [CodeExamples(**example) for example in code_examples_data]
        created_code_examples = service.code_example_service.create_code_examples(
            code_examples, resource_id, current_user
        )
        converted = CodeExampleResponse.model_validate(created_code_examples)
        return [converted]
    except ValueError as e:
        logger.error(f"Value error while adding code examples: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{resource_id}/code_examples/{code_example_id}",
    status_code=200,
    description="Update a code example of a resource",
    response_model=CodeExampleResponse,
    response_model_exclude_none=True,
    tags=["admin"],
)
async def update_code_example(
    resource_id: uuid.UUID,
    code_example_id: uuid.UUID,
    code_example_req: UpdateCodeExampleRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    service: ResourceService = Depends(get_resource_service),
) -> CodeExampleResponse:
    try:
        code_example_data = code_example_req.model_dump()
        code_example = code_example_data.model_dump()
        updated_code_example = service.code_example_service.update_code_example(
            resource_id=resource_id,
            code_example_id=code_example_id,
            code_example=code_example,
            user=current_user,
        )
        converted = CodeExampleResponse.model_validate(updated_code_example)
        return converted
    except ValueError as e:
        logger.error(f"Value error while updating code example: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{resource_id}/examples",
    status_code=201,
    description="Add examples to a resource",
    response_model=List[ExampleResponse],
    response_model_exclude_none=True,
    tags=["admin"],
)
async def add_examples(
    resource_id: uuid.UUID,
    examples_req: List[ExampleRequest],
    current_user: Annotated[User, Depends(authenticate_user)],
    service: ResourceService = Depends(get_resource_service),
) -> List[ExampleResponse]:
    try:
        examples_data = examples_req.model_dump()
        examples = [Examples(**example) for example in examples_data]
        created_examples = service.example_service.create_examples(
            examples, resource_id, current_user
        )
        logger.info(f"Response data: {created_examples}")
        return [ExampleResponse.model_validate(example) for example in created_examples]
    except ValueError as e:
        logger.error(f"Value error while adding examples: {e}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{resource_id}/examples/{example_id}",
    status_code=200,
    description="Update an example of a resource",
    response_model=ExampleResponse,
    response_model_exclude_none=True,
    tags=["admin"],
)
async def update_example(
    example_id: uuid.UUID,
    example_req: UpdateExampleRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    service: ResourceService = Depends(get_resource_service),
) -> ExampleResponse:
    try:
        example_data = example_req.model_dump()
        example = Examples(**example_data)
        updated_example = service.example_service.update_example(
            example_id, example, current_user
        )
        return ExampleResponse.model_validate(updated_example)
    except ValueError as e:
        logger.error(f"Value error while updating example: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
