# src/services/news_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.news import NewsTable, NewsCreate
from typing import List, Optional

class NewsService:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[NewsTable]:
        # Sắp xếp tin tức mới nhất lên đầu (desc)
        result = await db.execute(select(NewsTable).order_by(NewsTable.published_at.desc()))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, news_id: int) -> Optional[NewsTable]:
        result = await db.execute(select(NewsTable).where(NewsTable.news_id == news_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: NewsCreate) -> NewsTable:
        new_news = NewsTable(**data.model_dump())
        db.add(new_news)
        await db.flush() # Để lấy được id vừa sinh ra
        return new_news

    @staticmethod
    async def update(db: AsyncSession, news_id: int, data: NewsCreate) -> Optional[NewsTable]:
        news = await NewsService.get_by_id(db, news_id)
        if not news:
            return None
            
        for key, value in data.model_dump().items():
            setattr(news, key, value)
            
        await db.flush()
        return news

    @staticmethod
    async def delete(db: AsyncSession, news_id: int) -> bool:
        news = await NewsService.get_by_id(db, news_id)
        if not news:
            return False
            
        await db.delete(news)
        await db.flush()
        return True