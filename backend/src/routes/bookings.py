from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.db import get_db
from src.controllers.booking_controller import BookingController
from src.models.booking import BookingReserveRequest, BookingResponse, BookingDetailResponse
from src.middlewares.auth import get_current_user, verify_admin
from src.models.user import UserTable

router = APIRouter()

@router.get("/admin", dependencies=[Depends(verify_admin)])
async def get_all_bookings_admin(
    page: int = 1,
    limit: int = 12,
    search: str = "",
    status: str = "all",
    db: AsyncSession = Depends(get_db)
):
    return await BookingController.get_admin_bookings(db, page, limit, search, status)

@router.put("/admin/{booking_id}/status", dependencies=[Depends(verify_admin)])
async def update_booking_status_admin(
    booking_id: int, 
    status: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    return await BookingController.update_booking_status(db, booking_id, status)

@router.post("/reserve", response_model=BookingResponse)
async def reserve_booking(
    payload: BookingReserveRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: UserTable = Depends(get_current_user)
):
    return await BookingController.reserve_booking(db, current_user.user_id, payload)

@router.get("/{booking_id}", response_model=BookingDetailResponse)
async def get_booking_detail(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserTable = Depends(get_current_user)
):
    return await BookingController.get_booking_detail(db, current_user.user_id, booking_id)
