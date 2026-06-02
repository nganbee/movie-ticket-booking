# src/models/movie.py
from datetime import date
from typing import Optional
from sqlalchemy import Text, Integer, Date, Float
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from src.config.db import Base

# --- 1. SQLALCHEMY MODEL (Tạo bảng trên Supabase) ---
class MovieTable(Base):
    __tablename__ = "movies"

    movie_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    genre: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(Text, nullable=False)
    release_date: Mapped[date] = mapped_column(Date, nullable=False)
    poster_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    director: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    imdb_id: Mapped[Optional[str]] = mapped_column(Text, unique=True, nullable=True)
    imdb_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    imdb_votes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

# --- 2. PYDANTIC SCHEMAS (Validate dữ liệu API) ---
class MovieBase(BaseModel):
    title: str
    duration: int
    genre: str
    language: str
    release_date: date
    poster_url: Optional[str] = None
    director: str
    status: str
    description: str
    imdb_id: Optional[str] = None
    imdb_rating: Optional[float] = None
    imdb_votes: Optional[int] = None

class MovieCreate(MovieBase):
    pass

class MovieResponse(MovieBase):
    movie_id: int
    showtimes: list[str] = []

    class Config:
        from_attributes = True