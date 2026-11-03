from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.services.auth_service import AuthenticatedUser, AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_auth_service = AuthService()


def get_auth_service() -> AuthService:
    return _auth_service


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthenticatedUser:
    return service.get_user_from_token(token)


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
