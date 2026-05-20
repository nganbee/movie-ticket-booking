# src/controllers/news_controller.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.news_service import NewsService
from src.models.news import NewsCreate

class NewsController:
    @staticmethod
    async def get_all_news(db: AsyncSession):
        """
        Xử lý logic lấy toàn bộ tin tức từ Supabase
        """
        return await NewsService.get_all(db)

    @staticmethod
    async def get_news_by_id(db: AsyncSession, news_id: int):
        """
        Xử lý logic lấy chi tiết một bài tin tức bằng ID (kiểu int)
        """
        news = await NewsService.get_by_id(db, news_id)
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Không tìm thấy bài viết yêu cầu"
            )
        return news

    @staticmethod
    async def create_news(db: AsyncSession, data: NewsCreate):
        """
        Xử lý logic thêm tin tức mới (Admin)
        """
        return await NewsService.create(db, data)

    @staticmethod
    async def update_news(db: AsyncSession, news_id: int, data: NewsCreate):
        """
        Xử lý logic cập nhật tin tức (Admin)
        """
        updated_news = await NewsService.update(db, news_id, data)
        if not updated_news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Không tìm thấy bài tin tức để cập nhật"
            )
        return updated_news

    @staticmethod
    async def delete_news(db: AsyncSession, news_id: int):
        """
        Xử lý logic xóa tin tức (Admin)
        """
        success = await NewsService.delete(db, news_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Không tìm thấy bài tin tức để xóa"
            )
        return None