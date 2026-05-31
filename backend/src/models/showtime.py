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

class TheaterTable(Base):
    __tablename__ = "theaters"

    theater_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)

    rooms: Mapped[list["RoomTable"]] = relationship("RoomTable", back_populates="theater")


class RoomTable(Base):
    __tablename__ = "rooms"

    room_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    theater_id: Mapped[int] = mapped_column(Integer, ForeignKey("theaters.theater_id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    seat_capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    theater: Mapped["TheaterTable"] = relationship("TheaterTable", back_populates="rooms")
    showtimes: Mapped[list["ShowtimeTable"]] = relationship("ShowtimeTable", back_populates="room")


class ShowtimeTable(Base):
    __tablename__ = "showtimes"

    showtime_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.movie_id"), nullable=False)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.room_id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    day_type: Mapped[str] = mapped_column(Text, nullable=False)  # 'Weekday' | 'Weekend' | 'Holiday'

    room: Mapped["RoomTable"] = relationship("RoomTable", back_populates="showtimes")


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
    room: Optional[RoomResponse] = None

    class Config:
        from_attributes = True
