# src/models/showtime.py
from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from src.config.db import Base


# ─────────────────────────────────────────────
# 1. SQLALCHEMY TABLES
# ─────────────────────────────────────────────

from src.models.theater import TheaterTable, RoomTable, ShowtimeTable


# ─────────────────────────────────────────────
# 2. PYDANTIC SCHEMAS
# ─────────────────────────────────────────────

class TheaterResponse(BaseModel):
    theater_id: int
    name: str
    address: str

    class Config:
        from_attributes = True


class RoomResponse(BaseModel):
    room_id: int
    theater_id: int
    name: str
    seat_capacity: int
    theater: Optional[TheaterResponse] = None

    class Config:
        from_attributes = True


class ShowtimeCreate(BaseModel):
    """Schema dùng cho một suất chiếu trong Bulk Insert"""
    movie_id: int
    room_id: int
    start_time: datetime
    end_time: datetime
    day_type: str  # 'Weekday' | 'Weekend' | 'Holiday'
    format: str = "2D"


class ShowtimeBulkCreate(BaseModel):
    """Schema cho POST /showtimes/bulk"""
    showtimes: list[ShowtimeCreate]


class ShowtimeResponse(BaseModel):
    showtime_id: int
    movie_id: int
    room_id: int
    start_time: datetime
    end_time: datetime
    day_type: str
    format: str = "2D"

    class Config:
        from_attributes = True


class ShowtimeDetailResponse(BaseModel):
    """Trả về chi tiết suất chiếu kèm thông tin phòng chiếu"""
    showtime_id: int
    movie_id: int
    room_id: int
    start_time: datetime
    end_time: datetime
    day_type: str
    format: str = "2D"
    room: Optional[RoomResponse] = None

    class Config:
        from_attributes = True
