# src/routes/news.py
from fastapi import APIRouter, status, Depends, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.news import UnifiedNewsResponse, UnifiedNewsCreate
from src.controllers.news_controller import NewsController
from src.config.db import get_db
from src.middlewares.auth import verify_admin

router = APIRouter()

# --- PUBLIC ENDPOINTS ---

@router.get("/", response_model=List[UnifiedNewsResponse])
async def get_news(db: AsyncSession = Depends(get_db)):
    """
    API lấy danh sách toàn bộ tin tức và khuyến mãi
    """
    return await NewsController.get_all_news(db)


# --- ADMIN ENDPOINTS ---

@router.post("/", response_model=UnifiedNewsResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_admin)])
async def create_news(news_data: UnifiedNewsCreate, db: AsyncSession = Depends(get_db)):
    """
    API (Admin) Tạo mới một bài tin tức hoặc khuyến mãi
    """
    return await NewsController.create_news(db, news_data)

@router.put("/{id}", response_model=UnifiedNewsResponse, dependencies=[Depends(verify_admin)])
async def update_news(id: int, news_data: UnifiedNewsCreate, db: AsyncSession = Depends(get_db)):
    """
    API (Admin) Cập nhật bài tin tức theo ID
    """
    return await NewsController.update_news(db, id, news_data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_admin)])
async def delete_news(id: int, type: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    API (Admin) Xóa bài tin tức theo ID và loại (type)
    """
    return await NewsController.delete_news(db, id, type)