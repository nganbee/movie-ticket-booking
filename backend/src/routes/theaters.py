from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from src.config.db import get_db
from src.models.theater import TheaterTable, RoomTable

router = APIRouter()

@router.get("/", summary="Lấy danh sách rạp và phòng chiếu")
async def get_theaters(db: AsyncSession = Depends(get_db)):
    stmt = select(TheaterTable).options(selectinload(TheaterTable.rooms))
    result = await db.execute(stmt)
    theaters = result.scalars().all()
    
    # Format response
    response = []
    for t in theaters:
        response.append({
            "theater_id": t.theater_id,
            "name": t.name,
            "address": t.address,
            "rooms": [
                {
                    "room_id": r.room_id,
                    "name": r.name,
                    "seat_capacity": r.seat_capacity
                } for r in t.rooms
            ]
        })
    return response
