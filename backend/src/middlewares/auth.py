# src/middlewares/auth.py
from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.db import get_db
from src.models.user import UserTable
from src.services.auth_service import AuthService

# ─── HTTPBearer scheme (tự động hiển thị lock icon trong Swagger UI) ──────────
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserTable:
    """
    Dependency: Xác thực JWT token từ Authorization header.
    Trả về UserTable nếu hợp lệ.
    Raises HTTP 401 nếu token invalid/expired/revoked.
    """
    token = credentials.credentials
    payload = AuthService.decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không chứa thông tin người dùng",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await AuthService.get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Dependency: Trả về raw JWT string (dùng cho logout)."""
    return credentials.credentials


def verify_admin(current_user: UserTable = Depends(get_current_user)) -> UserTable:
    """
    Dependency: Kiểm tra quyền Admin.
    Thay thế hardcoded admin_key cũ bằng JWT role-based check.
    Raises HTTP 403 nếu không phải admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện chức năng này"
        )
    return current_user
