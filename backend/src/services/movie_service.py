# src/services/movie_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from typing import List, Optional, Tuple
from datetime import datetime, timezone
from src.models.movie import MovieTable, MovieCreate
from src.models.showtime import ShowtimeTable

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
        if status == "all":
            pass  # Trả về tất cả
        elif status:
            base_stmt = base_stmt.where(MovieTable.status == status)
        else:
            # Mặc định chỉ trả về phim đang chiếu và sắp chiếu
            base_stmt = base_stmt.where(MovieTable.status.in_(["now_showing", "coming_soon"]))
            
        if genre:
            base_stmt = base_stmt.where(MovieTable.genre.ilike(f"%{genre}%"))

        # Sắp xếp: now_showing (n) > coming_soon (c) nên dùng desc() để now_showing lên trước
        # Sau đó sắp xếp theo ngày phát hành mới nhất (desc)
        base_stmt = base_stmt.order_by(MovieTable.status.desc(), MovieTable.release_date.desc())

        # --- Đếm tổng số bản ghi (cho frontend biết tổng số trang) ---
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # --- Lấy dữ liệu theo trang ---
        offset = (page - 1) * limit
        paged_stmt = base_stmt.offset(offset).limit(limit)
        result = await db.execute(paged_stmt)
        movies = result.scalars().all()

        # --- Tự động đính kèm showtimes sắp chiếu ---
        if movies:
            movie_ids = [m.movie_id for m in movies]
            now_utc = datetime.now(timezone.utc)
            
            st_stmt = (
                select(ShowtimeTable.movie_id, ShowtimeTable.start_time)
                .where(
                    ShowtimeTable.movie_id.in_(movie_ids),
                    ShowtimeTable.start_time >= now_utc
                )
                .order_by(ShowtimeTable.start_time)
            )
            st_result = await db.execute(st_stmt)
            showtimes_data = st_result.all()
            
            # Gom nhóm theo movie_id và extract giờ
            st_map = {m_id: [] for m_id in movie_ids}
            for m_id, start_time in showtimes_data:
                # Đổi giờ UTC thành Local string HH:MM
                local_time = start_time.astimezone()
                time_str = local_time.strftime("%H:%M")
                if time_str not in st_map[m_id]: # Loại bỏ trùng lặp nếu cùng 1 giờ có nhiều phòng chiếu
                    st_map[m_id].append(time_str)
                    
            # Gán vào từng object movie
            for m in movies:
                # set property động để Pydantic đọc qua Config.from_attributes
                setattr(m, "showtimes", st_map[m.movie_id][:6]) # Trả về tối đa 6 khung giờ

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
            
        movie.status = "stopped_showing"
        await db.flush()
        return True