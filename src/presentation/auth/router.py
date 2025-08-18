import os
from typing import Optional

from fastapi import APIRouter, Response, Cookie, HTTPException, Depends

from application.auth.dto import TokenResponseDTO, LoginRequestDTO
from application.auth.service import AuthService
from presentation.dependencies import get_auth_service

auth_router = APIRouter(prefix="/v1/auth", tags=["Authentication"])
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")

@auth_router.post("/login", response_model=TokenResponseDTO)
def login(
    response: Response,
    login_data: LoginRequestDTO,
    auth_service: AuthService = Depends(get_auth_service), # Mock - swap on DI receiving Auth Service
):
    try:
        access_token, refresh_token = auth_service.login(login_data)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="strict",
            secure=True,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        return TokenResponseDTO(access_token=access_token)

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@auth_router.get("/logout")
def logout(response: Response):
    response.delete_cookie(key="refresh_token")

    return {"message": "Successfully logged out"}

@auth_router.get("/reissue_token", response_model=TokenResponseDTO)
def reissue_token(
    refresh_token: Optional[str] = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found in cookies!")

    try:
        new_access_token = auth_service.refresh_access_token(refresh_token)
        return TokenResponseDTO(access_token=new_access_token)

    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Something went wrong while refreshing access "
                                                    f"token - {str(e)}")

