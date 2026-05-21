# src/services/auth_service.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
import bcrypt

from src.config.settings import settings
from src.models.user import UserTable, UserRegister

# ─── In-memory token blacklist (logout) ──────────────────────────────────────
# Cho production, nên dùng Redis hoặc bảng DB riêng
_revoked_tokens: set[str] = set()


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


class AuthService:

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def hash_password(plain_password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def create_access_token(user_id: int, role: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expire,
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Giải mã JWT. Trả None nếu invalid hoặc đã bị revoke."""
        if token in _revoked_tokens:
            return None
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            return None

    @staticmethod
    def revoke_token(token: str) -> None:
        """Đưa token vào blacklist (logout)."""
        _revoked_tokens.add(token)

    # ── Business Logic ────────────────────────────────────────────────────────

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserTable]:
        result = await db.execute(select(UserTable).where(UserTable.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[UserTable]:
        result = await db.execute(select(UserTable).where(UserTable.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def register(db: AsyncSession, data: UserRegister) -> UserTable:
        """
        Đăng ký tài khoản mới.
        Raises ValueError nếu email đã tồn tại.
        """
        existing = await AuthService.get_user_by_email(db, data.email)
        if existing:
            raise ValueError("Email này đã được sử dụng")

        new_user = UserTable(
            full_name=data.full_name,
            email=data.email,
            hashed_password=AuthService.hash_password(data.password),
            phone=data.phone,
            role="user",
        )
        db.add(new_user)
        await db.flush()  # Để Supabase gán user_id trước khi return
        return new_user

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> tuple[UserTable, str]:
        """
        Đăng nhập.
        Trả về (user, access_token) nếu thành công.
        Raises ValueError với thông báo chung nếu sai, PermissionError nếu bị khóa.
        """
        user = await AuthService.get_user_by_email(db, email)

        # Kiểm tra tài khoản có bị khóa không
        if user and user.locked_until:
            if datetime.now(timezone.utc) < user.locked_until.replace(tzinfo=timezone.utc):
                remaining = (user.locked_until.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc))
                minutes = int(remaining.total_seconds() // 60) + 1
                raise PermissionError(
                    f"Tài khoản tạm thời bị khóa. Vui lòng thử lại sau {minutes} phút."
                )
            else:
                # Hết thời gian khóa, reset
                user.failed_login_attempts = 0
                user.locked_until = None

        # Kiểm tra thông tin đăng nhập
        if not user or not AuthService.verify_password(password, user.hashed_password):
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                    user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
                    user.failed_login_attempts = 0
                await db.flush()
            # Thông báo chung, không tiết lộ trường nào sai (bảo mật)
            raise ValueError("Email hoặc mật khẩu không chính xác")

        # Đăng nhập thành công: reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        await db.flush()

        token = AuthService.create_access_token(user.user_id, user.role)
        return user, token
