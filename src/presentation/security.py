import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from domain.user.model import User as DomainUser
from application.uow.interfaces import IUnitOfWork
from application.auth.interfaces import ITokenService

from presentation.dependencies import get_uow, get_token_service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        uow: IUnitOfWork = Depends(get_uow),
        token_service: ITokenService = Depends(get_token_service),
) -> DomainUser:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = token_service.decode_token(token)

        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id_str is None:
            raise credentials_exception

        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Access token required.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = uuid.UUID(user_id_str)

    except (JWTError, ValueError):
        raise credentials_exception

    async with uow:
        user = await uow.users.get_by_id(user_id)

        if user is None:
            raise credentials_exception

    return user