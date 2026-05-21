# src/models/user.py
from datetime import datetime
from typing import Optional
from sqlalchemy import Text, Integer, DateTime, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, EmailStr, field_validator
from src.config.db import Base


# ─────────────────────────────────────────────
# 1. SQLALCHEMY TABLE (tạo bảng trên Supabase)
# ─────────────────────────────────────────────
class UserTable(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(Text, nullable=False, default="user")
    # Lockout: theo FR-A3, khóa 15 phút sau 5 lần thất bại
    failed_login_attempts: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )


# ─────────────────────────────────────────────
# 2. PYDANTIC SCHEMAS
# ─────────────────────────────────────────────

class UserRegister(BaseModel):
    """Schema cho POST /auth/register"""
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Họ tên không được để trống")
        return v.strip()


class UserLogin(BaseModel):
    """Schema cho POST /auth/login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema cho PUT /user/profile"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    new_password: Optional[str] = None
    current_password: Optional[str] = None  # Bắt buộc khi đổi mật khẩu

    @field_validator("new_password")
    @classmethod
    def new_password_min_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 8:
            raise ValueError("Mật khẩu mới phải có ít nhất 8 ký tự")
        return v


class UserResponse(BaseModel):
    """Schema trả về thông tin user (không có password)"""
    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema trả về sau khi login thành công"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
