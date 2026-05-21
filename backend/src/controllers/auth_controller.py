# src/controllers/auth_controller.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import UserRegister, UserLogin, TokenResponse, UserResponse
from src.services.auth_service import AuthService


class AuthController:

    @staticmethod
    async def register(db: AsyncSession, data: UserRegister) -> UserResponse:
        """
        Đăng ký tài khoản mới.
        HTTP 409 nếu email đã tồn tại.
        """
        try:
            user = await AuthService.register(db, data)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        return UserResponse.model_validate(user)

    @staticmethod
    async def login(db: AsyncSession, data: UserLogin) -> TokenResponse:
        """
        Đăng nhập.
        HTTP 401 nếu sai thông tin.
        HTTP 403 nếu tài khoản bị khóa.
        """
        try:
            user, token = await AuthService.login(db, data.email, data.password)
        except PermissionError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    async def logout(token: str) -> dict:
        """Đăng xuất: thêm token vào blacklist."""
        AuthService.revoke_token(token)
        return {"message": "Đăng xuất thành công"}
