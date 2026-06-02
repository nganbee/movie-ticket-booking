# src/controllers/movie_controller.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math
from src.services.movie_service import MovieService
from src.models.movie import MovieCreate

class MovieController:
    @staticmethod
    async def get_movies(
        db: AsyncSession,
        status_filter: Optional[str],
        genre_filter: Optional[str],
        page: int = 1,
        limit: int = 12
    ):
        movies, total = await MovieService.get_all(db, status_filter, genre_filter, page, limit)
        return {
            "items": movies,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": math.ceil(total / limit) if limit > 0 else 1
        }

    @staticmethod
    async def get_movie_by_id(db: AsyncSession, movie_id: int):
        movie = await MovieService.get_by_id(db, movie_id)
        if not movie:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phim yêu cầu")
        return movie

    @staticmethod
    async def create_movie(db: AsyncSession, data: MovieCreate):
        return await MovieService.create(db, data)

    @staticmethod
    async def update_movie(db: AsyncSession, movie_id: int, data: MovieCreate):
        updated_movie = await MovieService.update(db, movie_id, data)
        if not updated_movie:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phim để cập nhật")
        return updated_movie

    @staticmethod
    async def delete_movie(db: AsyncSession, movie_id: int):
        success = await MovieService.delete(db, movie_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phim để xóa")
        return None