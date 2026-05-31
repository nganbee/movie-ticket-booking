# src/controllers/showtime_controller.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.services.showtime_service import ShowtimeService
from src.models.showtime import ShowtimeBulkCreate


class ShowtimeController:

    @staticmethod
    async def get_showtimes(
        db: AsyncSession,
        movie_id: Optional[int],
        date: Optional[str],
    ):
        return await ShowtimeService.get_all(db, movie_id, date)

    @staticmethod
    async def bulk_create(db: AsyncSession, data: ShowtimeBulkCreate):
        if not data.showtimes:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Danh sách suất chiếu không được để trống.",
            )
        try:
            created = await ShowtimeService.bulk_create(db, data.showtimes)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        return created

    @staticmethod
    async def delete_showtime(db: AsyncSession, showtime_id: int):
        success = await ShowtimeService.delete(db, showtime_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy suất chiếu ID={showtime_id}.",
            )
        return None
