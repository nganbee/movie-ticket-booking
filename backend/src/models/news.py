# src/models/news.py
from datetime import datetime
from typing import Optional
from sqlalchemy import Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.config.db import Base
from pydantic import BaseModel

# --- SQLALCHEMY MODEL (Tạo bảng trên Supabase) ---
class NewsTable(Base):
    __tablename__ = "movie_news"

    news_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

# --- PYDANTIC SCHEMAS (Validate API) ---
class NewsBase(BaseModel):
    movie_id: int
    title: str
    content: str
    image_url: Optional[str] = None

class NewsCreate(NewsBase):
    pass

class NewsResponse(NewsBase):
    news_id: int
    published_at: datetime
    
    class Config:
        from_attributes = True