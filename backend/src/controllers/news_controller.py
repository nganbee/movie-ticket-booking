# src/controllers/news_controller.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.news_service import NewsService
from src.models.news import UnifiedNewsCreate

class NewsController:
    @staticmethod
    async def get_all_news(db: AsyncSession):
        return await NewsService.get_all_unified(db)

    @staticmethod
    async def create_news(db: AsyncSession, data: UnifiedNewsCreate):
        return await NewsService.create_unified(db, data)

    @staticmethod
    async def update_news(db: AsyncSession, news_id: int, data: UnifiedNewsCreate):
        updated_news = await NewsService.update_unified(db, news_id, data)
        if not updated_news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Không tìm thấy bài viết để cập nhật"
            )
        return updated_news

    @staticmethod
    async def delete_news(db: AsyncSession, news_id: int, item_type: str):
        success = await NewsService.delete_unified(db, news_id, item_type)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Không tìm thấy bài viết để xóa"
            )
        return None