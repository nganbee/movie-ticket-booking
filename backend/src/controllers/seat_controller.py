from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException
from src.models.theater import SeatTable, ShowSeatTable, ShowtimeTable
from typing import List
from datetime import datetime, timezone, timedelta

class SeatController:
    @staticmethod
    async def get_seat_map(db: AsyncSession, showtime_id: int):
        stmt = (
            select(SeatTable, ShowSeatTable)
            .join(ShowSeatTable, SeatTable.seat_id == ShowSeatTable.seat_id)
            .where(ShowSeatTable.showtime_id == showtime_id)
            .order_by(SeatTable.seat_row, SeatTable.seat_num)
        )
        result = await db.execute(stmt)
        rows = result.all()
        
        if not rows:
            raise HTTPException(status_code=404, detail="Sơ đồ ghế không tồn tại hoặc chưa được tạo cho suất chiếu này.")
            
        seat_map = []
        now = datetime.now(timezone.utc)
        for seat, show_seat in rows:
            status = show_seat.status
            # Tự động nhả ghế nếu hết thời gian giữ
            if status == "Holding" and show_seat.hold_expires_at and show_seat.hold_expires_at < now:
                status = "Available"
                
            seat_map.append({
                "seat_id": seat.seat_id,
                "seat_row": seat.seat_row,
                "seat_num": seat.seat_num,
                "seat_type": seat.seat_type,
                "status": status
            })
        return seat_map

    @staticmethod
    async def hold_seats(db: AsyncSession, showtime_id: int, seat_ids: List[int]):
        now = datetime.now(timezone.utc)
        
        stmt = select(ShowSeatTable).where(
            ShowSeatTable.showtime_id == showtime_id,
            ShowSeatTable.seat_id.in_(seat_ids)
        )
        result = await db.execute(stmt)
        show_seats = result.scalars().all()
        
        if len(show_seats) != len(seat_ids):
            raise HTTPException(status_code=400, detail="Một hoặc nhiều ghế không hợp lệ trong suất chiếu này.")
            
        for ss in show_seats:
            if ss.status == "Sold":
                raise HTTPException(status_code=400, detail="Ghế đã được bán.")
            if ss.status == "Holding" and ss.hold_expires_at and ss.hold_expires_at > now:
                raise HTTPException(status_code=400, detail="Ghế đang được người khác giữ.")
                
        # Giữ ghế trong 10 phút (TTL)
        expires_at = now + timedelta(minutes=10)
        
        for ss in show_seats:
            ss.status = "Holding"
            ss.hold_expires_at = expires_at
            
        await db.commit()
        return {"message": "Đã giữ chỗ thành công", "expires_at": expires_at}
