from datetime import datetime
from typing import Optional, List
from sqlalchemy import Text, Integer, ForeignKey, DateTime, Float, BIGINT, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.config.db import Base
from pydantic import BaseModel

class BookingTable(Base):
    __tablename__ = "bookings"
    booking_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False) 
    showtime_id: Mapped[int] = mapped_column(ForeignKey("showtimes.showtime_id"), nullable=False)
    booking_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_price: Mapped[int] = mapped_column(BIGINT, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False) # pending, paid, cancelled

class PaymentTable(Base):
    __tablename__ = "payments"
    payment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.booking_id"), nullable=False)
    payment_method: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[float] = mapped_column(Float(53), nullable=False)
    payment_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    transaction_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

class BookingItemTable(Base):
    __tablename__ = "booking_items"
    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.booking_id"), nullable=False)
    show_seat_id: Mapped[int] = mapped_column(ForeignKey("show_seats.show_seat_id"), nullable=False)
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)
    rule_id: Mapped[int] = mapped_column(ForeignKey("pricing_rules.rule_id"), nullable=False)

class ETicketTable(Base):
    __tablename__ = "etickets"
    ticket_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("booking_items.item_id"), nullable=False)
    qr_code: Mapped[str] = mapped_column(Text, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)

class BookingReserveRequest(BaseModel):
    showtime_id: int
    seat_ids: List[int]

class BookingResponse(BaseModel):
    booking_id: int
    total_price: int
    status: str
    
    class Config:
        from_attributes = True

class BookingDetailResponse(BaseModel):
    booking_id: int
    total_price: int
    status: str
    movie_title: str
    room_name: str
    showtime_start: str
    seats: List[str]
    
    class Config:
        from_attributes = True
