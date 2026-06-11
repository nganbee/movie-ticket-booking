from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import Text, Integer, Date, ForeignKey, DateTime, Float, String, CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.config.db import Base
from pydantic import BaseModel

class TheaterTable(Base):
    __tablename__ = "theaters"
    theater_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)

    rooms: Mapped[List["RoomTable"]] = relationship("RoomTable", back_populates="theater")

class RoomTable(Base):
    __tablename__ = "rooms"
    room_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    theater_id: Mapped[int] = mapped_column(ForeignKey("theaters.theater_id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    seat_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    grid_rows: Mapped[int] = mapped_column(Integer, nullable=False, server_default="10")
    grid_cols: Mapped[int] = mapped_column(Integer, nullable=False, server_default="12")

    theater: Mapped["TheaterTable"] = relationship("TheaterTable", back_populates="rooms")
    seats: Mapped[List["SeatTable"]] = relationship("SeatTable", back_populates="room")
    showtimes: Mapped[List["ShowtimeTable"]] = relationship("ShowtimeTable", back_populates="room")

class SeatTable(Base):
    __tablename__ = "seats"
    seat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.room_id"), nullable=False)
    seat_row: Mapped[str] = mapped_column(String(2), nullable=False)
    seat_num: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_type: Mapped[str] = mapped_column(Text, nullable=False) # 'Standard', 'VIP'

    room: Mapped["RoomTable"] = relationship("RoomTable", back_populates="seats")

class ShowtimeTable(Base):
    __tablename__ = "showtimes"
    showtime_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.room_id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    day_type: Mapped[str] = mapped_column(Text, nullable=False) # 'Weekday', 'Weekend'
    format: Mapped[str] = mapped_column(Text, nullable=False, server_default="2D")

    room: Mapped["RoomTable"] = relationship("RoomTable", back_populates="showtimes")

class ShowSeatTable(Base):
    __tablename__ = "show_seats"
    show_seat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    showtime_id: Mapped[int] = mapped_column(ForeignKey("showtimes.showtime_id"), nullable=False)
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.seat_id"), nullable=False)
    booking_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bookings.booking_id"), nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False) # Available, Holding, Sold
    hold_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class PricingRuleTable(Base):
    __tablename__ = "pricing_rules"
    rule_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    seat_type: Mapped[str] = mapped_column(Text, nullable=False)
    day_type: Mapped[str] = mapped_column(Text, nullable=False)
    format: Mapped[str] = mapped_column(Text, nullable=False, server_default='2D')
    multiplier: Mapped[float] = mapped_column(Float, nullable=False)
    base_price: Mapped[int] = mapped_column(Integer, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date] = mapped_column(Date, nullable=False)

# Pydantic Schemas for Theater/Seats
class SeatResponse(BaseModel):
    seat_id: int
    seat_row: str
    seat_num: int
    seat_type: str
    status: str
    price: int = 70000
    
    class Config:
        from_attributes = True

class ShowSeatHoldRequest(BaseModel):
    showtime_id: int
    seat_ids: List[int]
