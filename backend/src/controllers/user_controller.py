# src/controllers/user_controller.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import UserUpdate, UserResponse
from src.services.user_service import UserService
from src.controllers.booking_controller import BookingController


class UserController:

    @staticmethod
    async def get_profile(db: AsyncSession, user_id: int) -> UserResponse:
        """Lấy thông tin profile. HTTP 404 nếu không tìm thấy user."""
        user = await UserService.get_profile(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy tài khoản người dùng"
            )
        return UserResponse.model_validate(user)

    @staticmethod
    async def update_profile(db: AsyncSession, user_id: int, data: UserUpdate) -> UserResponse:
        """
        Cập nhật thông tin cá nhân.
        HTTP 400 nếu mật khẩu hiện tại sai hoặc thiếu.
        HTTP 404 nếu user không tồn tại.
        """
        try:
            user = await UserService.update_profile(db, user_id, data)
        except LookupError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return UserResponse.model_validate(user)

    @staticmethod
    async def get_history(db: AsyncSession, user_id: int) -> list:
        """Lấy lịch sử đặt vé của user."""
        return await BookingController.get_user_bookings(db, user_id)
