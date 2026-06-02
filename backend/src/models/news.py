# src/models/news.py
from datetime import datetime
from typing import Optional
from sqlalchemy import Text, DateTime, Integer, Boolean, ForeignKey, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from src.config.db import Base
from pydantic import BaseModel

# ==========================================
# 1. MOVIE NEWS (TIN PHIM)
# ==========================================
class MovieNewsTable(Base):
    __tablename__ = "movie_news"

    news_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movie_id: Mapped[Optional[int]] = mapped_column(ForeignKey("movies.movie_id"), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

# ==========================================
# 2. PROMOTIONS (KHUYẾN MÃI & THÔNG BÁO)
# ==========================================
class PromotionTable(Base):
    __tablename__ = "promotions"

    promo_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="Khuyến Mãi") # Khuyến Mãi, Thông Báo
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    discount_percent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    banner_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Draft") # Draft, Published
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

# ==========================================
# 3. USER NOTIFICATIONS (THÔNG BÁO CHO USER)
# ==========================================
class UserNotificationTable(Base):
    __tablename__ = "user_notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    promo_id: Mapped[int] = mapped_column(ForeignKey("promotions.promo_id", ondelete="CASCADE"), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

# ==========================================
# PYDANTIC SCHEMAS
# ==========================================
class MovieNewsBase(BaseModel):
    movie_id: Optional[int] = None
    title: str
    content: str
    image_url: Optional[str] = None

class MovieNewsResponse(MovieNewsBase):
    news_id: int
    published_at: datetime
    class Config:
        from_attributes = True

class PromotionBase(BaseModel):
    type: str
    title: str
    content: str
    discount_percent: Optional[int] = None
    banner_url: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "Draft"

class PromotionResponse(PromotionBase):
    promo_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class UserNotificationResponse(BaseModel):
    id: int
    user_id: int
    promo_id: int
    is_read: bool
    created_at: datetime
    promotion: Optional[PromotionResponse] = None # Include related promo info when returning to user
    class Config:
        from_attributes = True

# ==========================================
# UNIFIED SCHEMAS (Cho Admin Dashboard)
# ==========================================
class UnifiedNewsCreate(BaseModel):
    title: str
    content: str
    type: str # Khuyến Mãi, Thông Báo, Tin Phim
    status: str = "Draft"
    publishDate: Optional[str] = None
    thumbnail: Optional[str] = None
    movieId: Optional[int] = None

class UnifiedNewsResponse(BaseModel):
    id: int
    title: str
    content: str
    type: str
    status: str
    publishDate: Optional[str] = None
    thumbnail: Optional[str] = None
    movieId: Optional[int] = None