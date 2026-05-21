# src/routes/auth.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.db import get_db
from src.models.user import UserRegister, UserLogin, UserResponse, TokenResponse
from src.controllers.auth_controller import AuthController
from src.middlewares.auth import get_current_token

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
    description="Tạo tài khoản người dùng mới. Email phải chưa tồn tại trong hệ thống. Mật khẩu tối thiểu 8 ký tự và sẽ được mã hóa bằng bcrypt.",
)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await AuthController.register(db, data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Đăng nhập",
    description="Xác thực email và mật khẩu. Trả về JWT access token. Tài khoản bị khóa 15 phút sau 5 lần thất bại liên tiếp.",
)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await AuthController.login(db, data)


@router.post(
    "/logout",
    summary="Đăng xuất",
    description="Hủy JWT token hiện tại bằng cách đưa vào blacklist. Token sẽ không còn hợp lệ ngay lập tức.",
)
async def logout(token: str = Depends(get_current_token)):
    return await AuthController.logout(token)
