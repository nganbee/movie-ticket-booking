from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.db import get_db
from src.controllers.booking_controller import BookingController
from src.models.booking import BookingReserveRequest, BookingResponse, BookingDetailResponse
from src.middlewares.auth import get_current_user
from src.models.user import UserTable

router = APIRouter()

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
