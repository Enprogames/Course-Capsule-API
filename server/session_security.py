import time
from typing import Optional, Union

from pydantic import BaseModel
from jose import JWTError, jwt
from fastapi.security import OAuth2
from fastapi import HTTPException, status, Request, Response, Cookie
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel

from server.models import UserRole


# Secret key for JWT
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"


class TokenData(BaseModel):
    user_id: int
    role: UserRole


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        # changed to accept access token from httpOnly Cookie
        authorization: str = request.cookies.get("access_token")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


def sign_jwt(user_id: int, role: UserRole) -> dict[str, any]:
    """Sign a JWT token with the username"""
    payload = {
        'sub': str(user_id),
        'exp': time.time() + 600,
        'iat': time.time(),
        'role': str(role.value)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> Union[TokenData, None]:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if decoded_token['exp'] < time.time():
            return None
        else:
            return TokenData(user_id=decoded_token['sub'], role=UserRole(int(decoded_token['role'])))
    except JWTError:
        return None
