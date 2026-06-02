# src/services/showtime_service.py
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, delete
from sqlalchemy.orm import selectinload

from src.models.showtime import ShowtimeTable, RoomTable, TheaterTable, ShowtimeCreate


class ShowtimeService:

    @staticmethod
    async def get_all(
        db: AsyncSession,
        movie_id: Optional[int] = None,
        date: Optional[str] = None,
    ) -> list[ShowtimeTable]:
        """
        Lấy danh sách suất chiếu.
        - movie_id: lọc theo phim
        - date: lọc theo ngày chiếu (format 'YYYY-MM-DD')
        """
        stmt = (
            select(ShowtimeTable)
            .options(
                selectinload(ShowtimeTable.room).selectinload(RoomTable.theater)
            )
            .order_by(ShowtimeTable.start_time)
        )

        if movie_id:
            stmt = stmt.where(ShowtimeTable.movie_id == movie_id)

        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
                stmt = stmt.where(
                    ShowtimeTable.start_time >= datetime.combine(target_date, datetime.min.time()).astimezone(),
                    ShowtimeTable.start_time < datetime.combine(target_date, datetime.max.time()).replace(microsecond=0).astimezone(),
                )
            except ValueError:
                pass  # Bỏ qua nếu format ngày sai, trả về tất cả

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def check_conflict(
        db: AsyncSession,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_showtime_id: Optional[int] = None,
    ) -> Optional[ShowtimeTable]:
        """
        Kiểm tra xem có suất chiếu nào trong cùng phòng bị trùng lịch không.
        Hai suất được coi là trùng khi: start_A < end_B AND start_B < end_A
        Trả về ShowtimeTable bị trùng nếu có, None nếu không.
        """
        stmt = select(ShowtimeTable).where(
            and_(
                ShowtimeTable.room_id == room_id,
                ShowtimeTable.start_time < end_time,
                ShowtimeTable.end_time > start_time,
            )
        )
        if exclude_showtime_id:
            stmt = stmt.where(ShowtimeTable.showtime_id != exclude_showtime_id)

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def bulk_create(
        db: AsyncSession,
        showtimes_data: list[ShowtimeCreate],
    ) -> list[ShowtimeTable]:
        """
        Bulk Insert nhiều suất chiếu.
        - Kiểm tra xung đột với dữ liệu trong DB.
        - Kiểm tra xung đột chéo giữa các phần tử trong danh sách gửi lên.
        - Raise ValueError với thông tin chi tiết nếu phát hiện xung đột.
        """
        errors = []

        # 1. Kiểm tra xung đột với DB
        for i, s in enumerate(showtimes_data):
            conflict = await ShowtimeService.check_conflict(db, s.room_id, s.start_time, s.end_time)
            if conflict:
                errors.append(
                    f"Suất chiếu #{i+1} (phòng {s.room_id}, {s.start_time} - {s.end_time}) "
                    f"bị trùng với suất chiếu ID={conflict.showtime_id} đã tồn tại trong hệ thống."
                )

        # 2. Kiểm tra xung đột chéo trong chính danh sách gửi lên
        for i in range(len(showtimes_data)):
            for j in range(i + 1, len(showtimes_data)):
                a, b = showtimes_data[i], showtimes_data[j]
                if a.room_id == b.room_id:
                    # Hai suất cùng phòng, kiểm tra overlap
                    if a.start_time < b.end_time and b.start_time < a.end_time:
                        errors.append(
                            f"Suất chiếu #{i+1} và #{j+1} trong danh sách gửi lên "
                            f"cùng phòng {a.room_id} và bị trùng lịch nhau."
                        )

        if errors:
            raise ValueError("\n".join(errors))

        # 3. Tất cả hợp lệ — thực hiện insert
        new_showtimes = []
        for s in showtimes_data:
            row = ShowtimeTable(
                movie_id=s.movie_id,
                room_id=s.room_id,
                start_time=s.start_time,
                end_time=s.end_time,
                day_type=s.day_type,
            )
            db.add(row)
            new_showtimes.append(row)

        await db.flush()  # Lưu Showtime để sinh ra showtime_id

        # Sparse Seating Optimization: Không pre-allocate các dòng 'Available' trong bảng show_seats.
        # Hệ thống sẽ ngầm hiểu các ghế không có dữ liệu là 'Available'.

        await db.commit()
        return new_showtimes

    @staticmethod
    async def get_by_id(db: AsyncSession, showtime_id: int) -> Optional[ShowtimeTable]:
        result = await db.execute(
            select(ShowtimeTable)
            .options(selectinload(ShowtimeTable.room).selectinload(RoomTable.theater))
            .where(ShowtimeTable.showtime_id == showtime_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(db: AsyncSession, showtime_id: int) -> bool:
        showtime = await ShowtimeService.get_by_id(db, showtime_id)
        if not showtime:
            return False
        await db.delete(showtime)
        await db.flush()
        return True
