# src/services/movie_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from src.models.movie import MovieTable, MovieCreate

class MovieService:
    @staticmethod
    async def get_all(db: AsyncSession, status: Optional[str] = None, genre: Optional[str] = None) -> List[MovieTable]:
        stmt = select(MovieTable)
        
        # Lọc theo trạng thái phim (đang chiếu / sắp chiếu)
        if status:
            stmt = stmt.where(MovieTable.status == status)
            
        # Lọc theo thể loại phim
        if genre:
            stmt = stmt.where(MovieTable.genre.ilike(f"%{genre}%"))
            
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, movie_id: int) -> Optional[MovieTable]:
        result = await db.execute(select(MovieTable).where(MovieTable.movie_id == movie_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: MovieCreate) -> MovieTable:
        new_movie = MovieTable(**data.model_dump())
        db.add(new_movie)
        await db.flush()  # Đồng bộ để Supabase tự sinh ID gán vào object
        return new_movie

    @staticmethod
    async def update(db: AsyncSession, movie_id: int, data: MovieCreate) -> Optional[MovieTable]:
        movie = await MovieService.get_by_id(db, movie_id)
        if not movie:
            return None
            
        # Cập nhật nhanh các field dữ liệu
        for key, value in data.model_dump().items():
            setattr(movie, key, value)
            
        await db.flush()
        return movie

    @staticmethod
    async def delete(db: AsyncSession, movie_id: int) -> bool:
        movie = await MovieService.get_by_id(db, movie_id)
        if not movie:
            return False
            
        await db.delete(movie)
        await db.flush()
        return True