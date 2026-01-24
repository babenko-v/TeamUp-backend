import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from dishka import Provider, Scope, provide

from domain.user.model import User as DomainUser

from application.uow.interfaces import IUnitOfWork
from application.auth.interfaces import ITokenService

from presentation.dependencies import get_uow, get_token_service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class AuthUserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_oauth2_scheme(self):
        return oauth2_scheme

    @provide(scope=Scope.REQUEST)
    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        uow: IUnitOfWork = Depends(get_uow),
        token_service: ITokenService = Depends(get_token_service),
    ) -> DomainUser:

        # Preparing exception in case handling error
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

            # Check type of token, if it's not a access, we will block access to endpoint
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
            # Retrieving user from database
            user = await uow.users.get_by_id(user_id)

            if user is None:
                raise credentials_exception

        return user


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        uow: IUnitOfWork = Depends(get_uow),
        token_service: ITokenService = Depends(get_token_service),
) -> DomainUser:

    # Preparing exception in case handling error
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

        # Check type of token, if it's not a access, we will block access to endpoint
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
        # Retrieving user from database
        user = await uow.users.get_by_id(user_id)

        if user is None:
            raise credentials_exception

    return user