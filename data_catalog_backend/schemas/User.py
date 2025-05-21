from typing import Optional

from pydantic import Field, field_validator

from data_catalog_backend.config import settings
from data_catalog_backend.schemas.basemodel import BaseModel


class User(BaseModel):
    name: str = Field(default="", description="Name of the user", min_length=1)
    email: str = Field(
        default="", description="Email of the user", min_length=1, max_length=100
    )
    preferred_username: Optional[str] = Field(
        default=None,
        description="Preferred username of the user",
        min_length=1,
        max_length=100,
    )
    roles: list[str] = Field()

    @field_validator("roles")
    def validate_roles(cls, roles):
        if settings.auth_required_role not in roles:
            raise ValueError("The role 'datacatalog_admin' is required.")
        return roles
