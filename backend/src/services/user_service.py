# src/services/user_service.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import UserTable, UserUpdate
from src.services.auth_service import AuthService


class UserService:

    @staticmethod
    async def get_profile(db: AsyncSession, user_id: int) -> Optional[UserTable]:
        """Lấy thông tin profile của user hiện tại."""
        result = await db.execute(select(UserTable).where(UserTable.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_profile(db: AsyncSession, user_id: int, data: UserUpdate) -> UserTable:
        """
        Cập nhật thông tin cá nhân: họ tên, SĐT, mật khẩu.
        Raises ValueError nếu current_password sai khi đổi mật khẩu.
        """
        user = await UserService.get_profile(db, user_id)
        if not user:
            raise LookupError("Không tìm thấy tài khoản người dùng")

        # Cập nhật họ tên
        if data.full_name is not None:
            user.full_name = data.full_name.strip()

        # Cập nhật số điện thoại
        if data.phone is not None:
            user.phone = data.phone.strip() or None

        # Đổi mật khẩu (yêu cầu cung cấp mật khẩu hiện tại)
        if data.new_password is not None:
            if not data.current_password:
                raise ValueError("Vui lòng cung cấp mật khẩu hiện tại để đổi mật khẩu mới")
            if not AuthService.verify_password(data.current_password, user.hashed_password):
                raise ValueError("Mật khẩu hiện tại không đúng")
            user.hashed_password = AuthService.hash_password(data.new_password)

        await db.flush()
        return user

    @staticmethod
    async def get_history(db: AsyncSession, user_id: int) -> list:
        """
        Lấy lịch sử đặt vé của user.
        Hiện tại trả về list rỗng — sẽ được join với bảng bookings khi module Booking được triển khai.
        """
        # TODO: Join với BookingTable khi module Booking (Phần 4) hoàn thành
        # stmt = (
        #     select(BookingTable)
        #     .where(BookingTable.user_id == user_id)
        #     .order_by(BookingTable.created_at.desc())
        # )
        # result = await db.execute(stmt)
        # return result.scalars().all()
        return []
