from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException
from src.models.theater import SeatTable, ShowSeatTable, ShowtimeTable
from typing import List
from datetime import datetime, timezone, timedelta

class SeatController:
    @staticmethod
    async def get_seat_map(db: AsyncSession, showtime_id: int):
        # Lấy thông tin suất chiếu để biết room_id
        st_res = await db.execute(select(ShowtimeTable).where(ShowtimeTable.showtime_id == showtime_id))
        showtime = st_res.scalar_one_or_none()
        if not showtime:
            raise HTTPException(status_code=404, detail="Không tìm thấy suất chiếu.")

        # LEFT OUTER JOIN SeatTable với ShowSeatTable
        stmt = (
            select(SeatTable, ShowSeatTable)
            .join(
                ShowSeatTable,
                (SeatTable.seat_id == ShowSeatTable.seat_id) & (ShowSeatTable.showtime_id == showtime_id),
                isouter=True
            )
            .where(SeatTable.room_id == showtime.room_id)
            .order_by(SeatTable.seat_row, SeatTable.seat_num)
        )
        result = await db.execute(stmt)
        rows = result.all()
        
        if not rows:
            raise HTTPException(status_code=404, detail="Sơ đồ ghế không tồn tại hoặc phòng chiếu chưa có ghế.")
            
        seat_map = []
        now = datetime.now(timezone.utc)
        for seat, show_seat in rows:
            status = show_seat.status if show_seat else "Available"
            
            # Tự động nhả ghế nếu hết thời gian giữ
            if status == "Holding" and show_seat and show_seat.hold_expires_at and show_seat.hold_expires_at < now:
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
        
        # Kiểm tra xem các ghế này có thuộc phòng của suất chiếu không
        st_res = await db.execute(select(ShowtimeTable).where(ShowtimeTable.showtime_id == showtime_id))
        showtime = st_res.scalar_one_or_none()
        if not showtime:
            raise HTTPException(status_code=404, detail="Không tìm thấy suất chiếu.")

        # Lấy danh sách các bản ghi ShowSeat hiện tại (nếu đã từng được Hold hoặc Sold)
        stmt = select(ShowSeatTable).where(
            ShowSeatTable.showtime_id == showtime_id,
            ShowSeatTable.seat_id.in_(seat_ids)
        )
        result = await db.execute(stmt)
        existing_show_seats = result.scalars().all()
        existing_map = {ss.seat_id: ss for ss in existing_show_seats}
        
        # Kiểm tra tính hợp lệ
        for s_id in seat_ids:
            if s_id in existing_map:
                ss = existing_map[s_id]
                if ss.status == "Sold":
                    raise HTTPException(status_code=400, detail="Ghế đã được bán.")
                if ss.status == "Holding" and ss.hold_expires_at and ss.hold_expires_at > now:
                    raise HTTPException(status_code=400, detail="Ghế đang được người khác giữ.")
                
        # Giữ ghế trong 10 phút (TTL)
        expires_at = now + timedelta(minutes=10)
        
        for s_id in seat_ids:
            if s_id in existing_map:
                ss = existing_map[s_id]
                ss.status = "Holding"
                ss.hold_expires_at = expires_at
            else:
                # Sparse Seating: Tạo mới bản ghi Holding nếu chưa tồn tại (tức là đang Available)
                new_ss = ShowSeatTable(
                    showtime_id=showtime_id,
                    seat_id=s_id,
                    status="Holding",
                    hold_expires_at=expires_at
                )
                db.add(new_ss)
            
        await db.commit()
        return {"message": "Đã giữ chỗ thành công", "expires_at": expires_at}
