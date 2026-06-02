# src/services/movie_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from typing import List, Optional, Tuple
from src.models.movie import MovieTable, MovieCreate

class MovieService:
    @staticmethod
    async def get_all(
        db: AsyncSession,
        status: Optional[str] = None,
        genre: Optional[str] = None,
        page: int = 1,
        limit: int = 12
    ) -> Tuple[List[MovieTable], int]:
        """
        Trả về (danh_sách_phim, tổng_số_phim).
        page bắt đầu từ 1, limit là số phần tử mỗi trang.
        """
        # --- Base condition ---
        base_stmt = select(MovieTable)
        if status:
            base_stmt = base_stmt.where(MovieTable.status == status)
        if genre:
            base_stmt = base_stmt.where(MovieTable.genre.ilike(f"%{genre}%"))

        # --- Đếm tổng số bản ghi (cho frontend biết tổng số trang) ---
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # --- Lấy dữ liệu theo trang ---
        offset = (page - 1) * limit
        paged_stmt = base_stmt.offset(offset).limit(limit)
        result = await db.execute(paged_stmt)
        movies = result.scalars().all()

        return movies, total

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