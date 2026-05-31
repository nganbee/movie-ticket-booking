# src/routes/showtimes.py
from fastapi import APIRouter, Depends, Query, status
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.db import get_db
from src.middlewares.auth import verify_admin
from src.models.showtime import ShowtimeDetailResponse, ShowtimeResponse, ShowtimeBulkCreate
from src.controllers.showtime_controller import ShowtimeController

router = APIRouter()


# ── PUBLIC ENDPOINTS ─────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[ShowtimeDetailResponse],
    summary="Lấy danh sách suất chiếu",
    description=(
        "Trả về danh sách suất chiếu kèm thông tin phòng chiếu và rạp. "
        "Có thể lọc theo `movie_id` hoặc `date` (format: YYYY-MM-DD)."
    ),
)
async def get_showtimes(
    movie_id: Optional[int] = Query(None, description="ID phim cần lọc"),
    date: Optional[str] = Query(None, description="Ngày chiếu, format YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
):
    return await ShowtimeController.get_showtimes(db, movie_id, date)


# ── ADMIN ENDPOINTS ───────────────────────────────────────────────────────────

@router.post(
    "/bulk",
    response_model=List[ShowtimeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="(Admin) Bulk Insert suất chiếu",
    description=(
        "Thêm nhiều suất chiếu cùng lúc. "
        "Hệ thống sẽ kiểm tra xung đột giờ chiếu trong cùng một phòng "
        "(cả với dữ liệu cũ trong DB và các suất chiếu khác trong cùng danh sách gửi lên). "
        "Nếu bất kỳ suất nào bị trùng lịch, toàn bộ request sẽ bị từ chối (trả về 400)."
    ),
    dependencies=[Depends(verify_admin)],
)
async def bulk_create_showtimes(
    data: ShowtimeBulkCreate,
    db: AsyncSession = Depends(get_db),
):
    return await ShowtimeController.bulk_create(db, data)


@router.delete(
    "/{showtime_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="(Admin) Hủy suất chiếu",
    description="Xóa một suất chiếu khỏi hệ thống theo ID. Trả về 404 nếu không tìm thấy.",
    dependencies=[Depends(verify_admin)],
)
async def delete_showtime(
    showtime_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await ShowtimeController.delete_showtime(db, showtime_id)
