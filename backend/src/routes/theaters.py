from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from src.config.db import get_db
from src.models.theater import TheaterTable, RoomTable
from src.middlewares.auth import verify_admin
from src.controllers.theater_controller import TheaterController

router = APIRouter()

@router.get("/", summary="Lấy danh sách rạp và phòng chiếu")
async def get_theaters(db: AsyncSession = Depends(get_db)):
    stmt = select(TheaterTable).options(
        selectinload(TheaterTable.rooms).selectinload(RoomTable.seats)
    )
    result = await db.execute(stmt)
    theaters = result.scalars().all()
    
    # Format response
    response = []
    for t in theaters:
        response.append({
            "id": t.theater_id,
            "name": t.name,
            "address": t.address,
            "rooms": [
                {
                    "id": r.room_id,
                    "branchId": t.theater_id,
                    "name": r.name,
                    "seat_capacity": r.seat_capacity,
                    "rows": r.grid_rows,
                    "cols": r.grid_cols,
                    "layout": { f"{s.seat_row}:{s.seat_num}": s.seat_type for s in r.seats }
                } for r in t.rooms
            ]
        })
    return response

@router.post("/", dependencies=[Depends(verify_admin)])
async def create_theater(
    name: str = Body(...),
    address: str = Body(...),
    db: AsyncSession = Depends(get_db)
):
    return await TheaterController.create_theater(db, name, address)

@router.put("/{theater_id}", dependencies=[Depends(verify_admin)])
async def update_theater(
    theater_id: int,
    name: str = Body(...),
    address: str = Body(...),
    db: AsyncSession = Depends(get_db)
):
    return await TheaterController.update_theater(db, theater_id, name, address)

@router.delete("/{theater_id}", dependencies=[Depends(verify_admin)])
async def delete_theater(
    theater_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await TheaterController.delete_theater(db, theater_id)

@router.post("/{theater_id}/rooms", dependencies=[Depends(verify_admin)])
async def create_room(
    theater_id: int,
    name: str = Body(...),
    rows: int = Body(...),
    cols: int = Body(...),
    layout: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    return await TheaterController.create_room(db, theater_id, name, rows, cols, layout)

@router.put("/rooms/{room_id}/layout", dependencies=[Depends(verify_admin)])
async def update_room_layout(
    room_id: int,
    rows: int = Body(...),
    cols: int = Body(...),
    layout: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    return await TheaterController.update_room_layout(db, room_id, rows, cols, layout)

@router.delete("/rooms/{room_id}", dependencies=[Depends(verify_admin)])
async def delete_room(
    room_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await TheaterController.delete_room(db, room_id)
