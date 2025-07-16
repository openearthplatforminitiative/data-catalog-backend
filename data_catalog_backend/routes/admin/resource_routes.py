import logging
import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import (
    get_resource_service,
)
from data_catalog_backend.models import (
    Resource,
    CodeExamples,
    Examples,
    Code,
)
from data_catalog_backend.routes.admin.authentication import authenticate_user
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.category import (
    CategoryResponse,
)
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
from data_catalog_backend.schemas.license import (
    LicenseResponse,
    LicenseRequest,
    UpdateLicenseRequest,
)
from data_catalog_backend.schemas.provider import ProviderResponse
from data_catalog_backend.schemas.resource import (
    ResourceRequest,
    ResourceResponse,
    UpdateResourceRequest,
    UpdateResourceCategoriesRequest,
    UpdateResourceCategoriesResponse,
    UpdateSpatialExtentRequest,
    UpdateSpatialExtentResponse,
    UpdateTemporalExtentRequest,
    UpdateTemporalExtentResponse,
    UpdateProviderResponse,
    UpdateProviderRequest,
)
from data_catalog_backend.schemas.spatial_extent import SpatialExtentResponse
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

        created = resource_service.create_resource(resource_req, current_user)

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
        updated_resource_data = update_resource_req.model_dump(exclude_unset=True)
        updated_resource = Resource(**updated_resource_data)

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


@router.put(
    "/{resource_id}/license",
    status_code=200,
    description="Update license of a resource",
    response_model_exclude_none=True,
    tags=["admin"],
    response_model=LicenseResponse,
)
async def update_license(
    resource_id: uuid.UUID,
    license_req: UpdateLicenseRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    resource_service: ResourceService = Depends(get_resource_service),
) -> LicenseResponse:
    license_data = license_req.model_dump()
    updated_license = resource_service.update_license(
        resource_id=resource_id,
        license_id=license_data["id"],
        current_user=current_user,
    )
    if updated_license:
        return LicenseResponse.model_validate(updated_license)
    raise HTTPException(
        status_code=404, detail="License not found or could not be updated"
    )


@router.put(
    "/{resource_id}/providers",
    status_code=200,
    description="Update providers for a resource",
    response_model_exclude_none=True,
    tags=["admin"],
    response_model=UpdateProviderResponse,
)
async def update_resource_providers(
    resource_id: uuid.UUID,
    providers_req: UpdateProviderRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    resource_service: ResourceService = Depends(get_resource_service),
) -> UpdateProviderResponse:

    providers_data = providers_req.model_dump()
    new_providers = resource_service.update_providers(
        resource_id=resource_id,
        provider_ids=providers_data["provider_ids"],
        current_user=current_user,
    )
    if new_providers:
        provider_responses = [
            ProviderResponse.model_validate(prov) for prov in new_providers
        ]
        return UpdateProviderResponse(providers=provider_responses)
    return UpdateProviderResponse(providers=[])


@router.put(
    "/{resource_id}/categories",
    status_code=200,
    description="Update categories of a resource",
    response_model=UpdateResourceCategoriesResponse,
    response_model_exclude_none=True,
    tags=["admin"],
)
async def update_resource_categories(
    resource_id: uuid.UUID,
    categories_req: UpdateResourceCategoriesRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    resource_service: ResourceService = Depends(get_resource_service),
) -> UpdateResourceCategoriesResponse:
    categories_data = categories_req.model_dump()

    updated_main_category = None
    try:
        if categories_data["main_category"]:
            main_category: uuid.UUID = categories_data["main_category"]
            updated_main_category = resource_service.set_main_category(
                category_id=main_category, resource_id=resource_id, user=current_user
            )

        additional_categories: List = categories_data["additional_categories"]

        # Override all existing additional categories with the new list
        updated_additional_categories = resource_service.override_additional_categories(
            resource_id=resource_id,
            categories=additional_categories,
            user=current_user,
        )
    except ValueError as e:
        logger.error(
            f"Value error while updating categories in resource {resource_id}: {e}"
        )
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating categories for resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    main_cat = None
    if updated_main_category:
        main_cat = CategoryResponse.model_validate(updated_main_category)

    additional_cats = []
    if updated_additional_categories:
        additional_cats = [
            CategoryResponse.model_validate(c) for c in updated_additional_categories
        ]
    return UpdateResourceCategoriesResponse(
        main_category=main_cat, additional_categories=additional_cats
    )


@router.put(
    "/{resource_id}/spatial_extent",
    status_code=200,
    description="Update spatial extent of a resource",
    response_model=UpdateSpatialExtentResponse,
    response_model_exclude_none=True,
    tags=["admin"],
)
async def update_spatial_extent(
    resource_id: uuid.UUID,
    spatial_extent_req: UpdateSpatialExtentRequest,
    resource_service: ResourceService = Depends(get_resource_service),
) -> UpdateSpatialExtentResponse:
    spatial_extent_data = spatial_extent_req.model_dump()
    new_spatial_extents = resource_service.update_spatial_extent(
        resource_id=resource_id,
        spatial_extent_ids=spatial_extent_data["spatial_extent_ids"],
    )
    if new_spatial_extents:
        spatial_extent_responses = [
            SpatialExtentResponse.model_validate(extent)
            for extent in new_spatial_extents
        ]
        return UpdateSpatialExtentResponse(spatial_extent=spatial_extent_responses)
    return UpdateSpatialExtentResponse(spatial_extent=[])


@router.put(
    "/{resource_id}/temporal_extent",
    status_code=200,
    description="Update temporal extent of a resource",
    response_model=UpdateTemporalExtentResponse,
    response_model_exclude_none=True,
    tags=["admin"],
)
async def update_temporal_extent(
    resource_id: uuid.UUID,
    temporal_extent_req: UpdateTemporalExtentRequest,
    resource_service: ResourceService = Depends(get_resource_service),
) -> UpdateTemporalExtentResponse:
    temporal_extent_data = temporal_extent_req.model_dump()
    new_temporal_extents = resource_service.update_temporal_extent(
        resource_id=resource_id,
        temporal_extent_ids=temporal_extent_data["temporal_extent_ids"],
    )
    if new_temporal_extents:
        temporal_extent_responses = [
            TemporalExtentResponse.model_validate(extent)
            for extent in new_temporal_extents
        ]
        return UpdateTemporalExtentResponse(temporal_extent=temporal_extent_responses)
    return UpdateTemporalExtentResponse(temporal_extent=[])


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

        code_examples = [
            CodeExamples(
                title=example.title,
                description=example.description,
                code=[
                    Code(language=code.language, source=code.source)
                    for code in example.code
                ],
            )
            for example in code_examples_req
        ]

        created_code_examples = service.code_example_service.create_code_examples(
            code_examples, resource_id, current_user
        )
        converted = [
            CodeExampleResponse.model_validate(code_example)
            for code_example in created_code_examples
        ]
        return converted
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
        existing_code_example = service.code_example_service.get_code_example(
            code_example_id
        )

        code_example_data = code_example_req.model_dump()
        code_example = CodeExamples(
            title=code_example_data["title"] or existing_code_example.title,
            description=code_example_data["description"]
            or existing_code_example.description,
            code=[
                (
                    Code(language=code["language"], source=code["source"])
                    if code.get("id") is None
                    else Code(
                        id=existing_code.id,
                        language=existing_code.language,
                        source=code["source"],
                    )
                )
                # Iterate over the list of new code snippets provided in the request
                for code in (code_example_data.get("code") or [])
                # Match each new code snippet with an existing code snippet by ID
                for existing_code in existing_code_example.code
                if existing_code.id == code.get("id")
            ],
        )

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
        examples_data = [example.model_dump() for example in examples_req]
        created_examples = service.example_service.create_examples(
            examples_data, resource_id, current_user
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
    description="Update an example of a resource",
    response_model=ExampleResponse,
    response_model_exclude_none=True,
    tags=["resources"],
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
        return ExampleResponse.model_validate(updated_example).model_dump()
    except ValueError as e:
        logger.error(f"Value error while updating example: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{resource_id}",
    status_code=204,
    description="Delete a resource from the metadata store",
    tags=["admin"],
    response_model_exclude_none=True,
)
async def delete_resource(
    resource_id: uuid.UUID,
    current_user: Annotated[User, Depends(authenticate_user)],
    resource_service: ResourceService = Depends(get_resource_service),
):
    try:
        logging.info(f"Deleting resource with id {resource_id}")
        resource_service.delete_resource(resource_id, current_user)

    except ValueError as ve:
        logger.warning(
            f"Validation error while deleting resource with ID: {resource_id} - {str(ve)}"
        )
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(
            f"Unexpected error while deleting resource with ID: {resource_id} - {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
