import logging
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from jwt import PyJWKClient
from pydantic import ValidationError

from data_catalog_backend.config import settings
from data_catalog_backend.dependencies import get_jwk_client
from data_catalog_backend.schemas.User import User

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.auth_url,
    tokenUrl=settings.token_url,
    auto_error=settings.api_domain != "localhost",
)

dummy_user = User(
    name="Dummy",
    email="dummy@openepi.io",
    preferred_username="dummy",
    roles=[settings.auth_required_role],
)


async def authenticate_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    jwk_client: Annotated[PyJWKClient, Depends(get_jwk_client)],
):
    if settings.api_domain == "localhost" and token is None:
        return dummy_user

    payload = jwt.decode(
        token,
        jwk_client.get_signing_key_from_jwt(token).key,
        algorithms=["RS256"],
        audience=settings.auth_client_id,
    )

    try:
        return User(
            name=payload.get("name", ""),
            email=payload.get("email", ""),
            preferred_username=payload.get("preferred_username", ""),
            roles=payload.get("realm_access", {}).get("roles", []),
        )
    except ValidationError as e:
        logger.warning(f"Autentication error: {e}")
        raise HTTPException(
            status_code=403,
            detail="User has not the required permissions",
        )
