from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from typing import List
from datetime import datetime, timezone

from src.models.booking import BookingTable, BookingItemTable, BookingReserveRequest
from src.models.theater import ShowSeatTable, SeatTable, PricingRuleTable, ShowtimeTable

class BookingController:
    @staticmethod
    async def reserve_booking(db: AsyncSession, user_id: int, payload: BookingReserveRequest):
        now = datetime.now(timezone.utc)
        
        stmt_st = select(ShowtimeTable).where(ShowtimeTable.showtime_id == payload.showtime_id)
        res_st = await db.execute(stmt_st)
        showtime = res_st.scalar_one_or_none()
        if not showtime:
            raise HTTPException(status_code=404, detail="Không tìm thấy suất chiếu.")
            
        day_type = showtime.day_type
        
        stmt_ss = (
            select(ShowSeatTable, SeatTable)
            .join(SeatTable, SeatTable.seat_id == ShowSeatTable.seat_id)
            .where(
                ShowSeatTable.showtime_id == payload.showtime_id,
                ShowSeatTable.seat_id.in_(payload.seat_ids)
            )
        )
        result = await db.execute(stmt_ss)
        rows = result.all()
        
        if len(rows) != len(payload.seat_ids):
            raise HTTPException(status_code=400, detail="Không tìm thấy thông tin của một hoặc nhiều ghế.")
            
        for ss, seat in rows:
            if ss.status == "Sold":
                raise HTTPException(status_code=400, detail=f"Ghế {seat.seat_row}{seat.seat_num} đã được bán.")
        
        # Load rules
        stmt_rules = select(PricingRuleTable).where(
            PricingRuleTable.effective_from <= now.date(),
            PricingRuleTable.effective_to >= now.date(),
            PricingRuleTable.day_type == day_type
        )
        res_rules = await db.execute(stmt_rules)
        rules = res_rules.scalars().all()
        rule_map = {r.seat_type: r for r in rules}
        
        total_price = 0
        items_to_create = []
        for ss, seat in rows:
            rule = rule_map.get(seat.seat_type)
            if not rule:
                raise HTTPException(status_code=500, detail=f"Không tìm thấy luật giá cho ghế {seat.seat_type} ngày {day_type}.")
                
            unit_price = int(rule.base_price * rule.multiplier)
            total_price += unit_price
            items_to_create.append({
                "show_seat_id": ss.show_seat_id,
                "unit_price": unit_price,
                "rule_id": rule.rule_id
            })
            
            ss.status = "Sold"
            ss.booking_id = None 
            
        booking = BookingTable(
            customer_id=user_id,
            showtime_id=payload.showtime_id,
            booking_date=now,
            total_price=total_price,
            status="pending"
        )
        db.add(booking)
        await db.flush() 
        
        for item in items_to_create:
            b_item = BookingItemTable(
                booking_id=booking.booking_id,
                show_seat_id=item["show_seat_id"],
                unit_price=item["unit_price"],
                rule_id=item["rule_id"]
            )
            db.add(b_item)
            
        for ss, seat in rows:
            ss.booking_id = booking.booking_id
            
        await db.commit()
        await db.refresh(booking)
        
        return {
            "booking_id": booking.booking_id,
            "total_price": booking.total_price,
            "status": booking.status
        }
