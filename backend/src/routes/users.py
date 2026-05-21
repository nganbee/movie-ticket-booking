# src/routes/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.config.db import get_db
from src.models.user import UserUpdate, UserResponse
from src.controllers.user_controller import UserController
from src.middlewares.auth import get_current_user
from src.models.user import UserTable

router = APIRouter()


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Lấy thông tin cá nhân",
    description="Trả về thông tin profile của người dùng đang đăng nhập. Yêu cầu JWT token hợp lệ.",
)
async def get_profile(
    current_user: UserTable = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserController.get_profile(db, current_user.user_id)


@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Cập nhật thông tin cá nhân",
    description=(
        "Cập nhật họ tên, số điện thoại và/hoặc mật khẩu. "
        "Khi đổi mật khẩu, phải cung cấp `current_password` để xác thực. "
        "Chỉ truyền các trường muốn cập nhật (partial update)."
    ),
)
async def update_profile(
    data: UserUpdate,
    current_user: UserTable = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserController.update_profile(db, current_user.user_id, data)


@router.get(
    "/history",
    summary="Lịch sử đặt vé",
    description=(
        "Trả về danh sách tất cả các vé đã đặt của người dùng, sắp xếp mới nhất trước. "
        "Bao gồm trạng thái thanh toán và thông tin suất chiếu. "
        "*(Chức năng đầy đủ sẽ được kích hoạt khi module Booking hoàn thành.)*"
    ),
    response_model=List[dict],
)
async def get_history(
    current_user: UserTable = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserController.get_history(db, current_user.user_id)
