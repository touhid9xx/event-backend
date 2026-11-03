from dataclasses import dataclass

from app.core.exceptions import UnauthorizedError
from app.core.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

# class InvalidCredentials(Exception):
#     """Raised when email/password do not match."""


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    email: str
    full_name: str
    is_active: bool


# Stage 2 only: hardcoded fake user, replaced by DB lookup in Stage 3.
_FAKE_USER = AuthenticatedUser(
    id=1,
    email="admin@example.com",
    full_name="Admin User",
    is_active=True,
)
_FAKE_PASSWORD_HASH = hash_password("admin123")


class AuthService:
    def authenticate(self, email: str, password: str) -> AuthenticatedUser:
        if email != _FAKE_USER.email:
            raise UnauthorizedError("Invalid email or password")
        if not verify_password(password, _FAKE_PASSWORD_HASH):
            raise UnauthorizedError("Invalid email or password")
        if not _FAKE_USER.is_active:
            raise UnauthorizedError("Invalid email or password")



        return _FAKE_USER

    def issue_token(self, user: AuthenticatedUser) -> str:
        return create_access_token(subject=str(user.id))

    def get_user_from_token(self, token: str) -> AuthenticatedUser:
        try:
            payload = decode_access_token(token)
        except TokenError as exc:
            raise UnauthorizedError(str(exc)) from exc

        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise UnauthorizedError("Invalid token payload")

        # Stage 2 only: return fake user if subject matches. Stage 3 replaces
        # this with a DB lookup by user_id.
        if int(subject) != _FAKE_USER.id:
            raise UnauthorizedError("User not found")
        return _FAKE_USER
