# src/routes/news.py
from fastapi import APIRouter, status, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.news import NewsResponse, NewsCreate
from src.controllers.news_controller import NewsController
from src.config.db import get_db
from src.middlewares.auth import verify_admin

router = APIRouter()

# --- PUBLIC ENDPOINTS ---

@router.get("/", response_model=List[NewsResponse])
async def get_news(db: AsyncSession = Depends(get_db)):
    """
    API lấy danh sách toàn bộ tin tức công khai
    """
    return await NewsController.get_all_news(db)

@router.get("/{id}", response_model=NewsResponse)
async def get_news_detail(id: int, db: AsyncSession = Depends(get_db)):
    """
    API lấy chi tiết một bài tin tức công khai bằng ID
    """
    return await NewsController.get_news_by_id(db, id)


# --- ADMIN ENDPOINTS ---

@router.post("/", response_model=NewsResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_admin)])
async def create_news(news_data: NewsCreate, db: AsyncSession = Depends(get_db)):
    """
    API (Admin) Tạo mới một bài tin tức
    """
    return await NewsController.create_news(db, news_data)

@router.put("/{id}", response_model=NewsResponse, dependencies=[Depends(verify_admin)])
async def update_news(id: int, news_data: NewsCreate, db: AsyncSession = Depends(get_db)):
    """
    API (Admin) Cập nhật bài tin tức theo ID
    """
    return await NewsController.update_news(db, id, news_data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_admin)])
async def delete_news(id: int, db: AsyncSession = Depends(get_db)):
    """
    API (Admin) Xóa bài tin tức theo ID
    """
    return await NewsController.delete_news(db, id)