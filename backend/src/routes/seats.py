from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.db import get_db
from src.controllers.seat_controller import SeatController
from src.models.theater import ShowSeatHoldRequest, SeatResponse
from typing import List
from src.middlewares.auth import get_current_user
from src.models.user import UserTable

router = APIRouter()

@router.get("/{showtime_id}", response_model=List[SeatResponse])
async def get_seat_map(showtime_id: int, db: AsyncSession = Depends(get_db)):
    return await SeatController.get_seat_map(db, showtime_id)

@router.post("/hold")
async def hold_seats(
    payload: ShowSeatHoldRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: UserTable = Depends(get_current_user)
):
    return await SeatController.hold_seats(db, payload.showtime_id, payload.seat_ids)
