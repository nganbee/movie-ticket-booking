from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from typing import List
from datetime import datetime, timezone, timedelta
import asyncio
from src.config.db import AsyncSessionLocal

from src.models.booking import BookingTable, BookingItemTable, BookingReserveRequest
from src.models.theater import ShowSeatTable, SeatTable, PricingRuleTable, ShowtimeTable, RoomTable
from src.models.movie import MovieTable
from src.models.booking import ETicketTable
from src.models.user import UserTable

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
            PricingRuleTable.day_type == day_type,
            PricingRuleTable.format == showtime.format
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
            
            # Chuyển từ Available sang Holding (nếu gọi trực tiếp reserve mà chưa hold),
            # hoặc gia hạn thời gian Holding. 
            # KHÔNG ĐỔI THÀNH SOLD KHI CHƯA THANH TOÁN
            ss.status = "Holding" 
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
        
        # Schedule timeout task
        asyncio.create_task(BookingController.timeout_booking_task(booking.booking_id))
        
        return {
            "booking_id": booking.booking_id,
            "total_price": booking.total_price,
            "status": booking.status
        }

    @staticmethod
    async def timeout_booking_task(booking_id: int):
        # Wait for 10 minutes
        await asyncio.sleep(600)
        async with AsyncSessionLocal() as db:
            await BookingController.cancel_booking(db, booking_id)

    @staticmethod
    async def cancel_booking(db: AsyncSession, booking_id: int):
        res = await db.execute(select(BookingTable).where(BookingTable.booking_id == booking_id))
        booking = res.scalars().first()
        
        if booking and booking.status == "pending":
            booking.status = "cancelled"
            
            # Release seats
            res_items = await db.execute(select(BookingItemTable).where(BookingItemTable.booking_id == booking_id))
            items = res_items.scalars().all()
            
            for item in items:
                res_ss = await db.execute(select(ShowSeatTable).where(ShowSeatTable.show_seat_id == item.show_seat_id))
                show_seat = res_ss.scalars().first()
                if show_seat:
                    show_seat.status = "Available"
                    show_seat.booking_id = None
                    
            await db.commit()

    @staticmethod
    async def start_background_cleanup_task():
        """
        Background task chạy mỗi 2 phút.
        Tìm các booking 'pending' đã quá hạn 10 phút và tự động huỷ.
        """
        import logging
        logger = logging.getLogger(__name__)
        while True:
            try:
                async with AsyncSessionLocal() as db:
                    # Tính mốc thời gian cách đây 10 phút
                    threshold = datetime.now(timezone.utc) - timedelta(minutes=10)
                    
                    # Tìm các booking pending quá hạn
                    stmt = select(BookingTable).where(
                        BookingTable.status == "pending",
                        BookingTable.booking_date <= threshold
                    )
                    res = await db.execute(stmt)
                    expired_bookings = res.scalars().all()
                    
                    for b in expired_bookings:
                        logger.info(f"Background Sweeper: Đang huỷ đơn hàng quá hạn {b.booking_id}")
                        await BookingController.cancel_booking(db, b.booking_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Lỗi trong Background Sweeper: {e}")
                
            try:
                await asyncio.sleep(120)  # Ngủ 2 phút rồi mới chạy lại
            except asyncio.CancelledError:
                break

    @staticmethod
    async def get_booking_detail(db: AsyncSession, user_id: int, booking_id: int):
        # Join bookings -> showtimes -> movies & rooms
        stmt = (
            select(BookingTable, MovieTable, RoomTable, ShowtimeTable)
            .join(ShowtimeTable, ShowtimeTable.showtime_id == BookingTable.showtime_id)
            .join(MovieTable, MovieTable.movie_id == ShowtimeTable.movie_id)
            .join(RoomTable, RoomTable.room_id == ShowtimeTable.room_id)
            .where(
                BookingTable.booking_id == booking_id,
                BookingTable.customer_id == user_id
            )
        )
        res = await db.execute(stmt)
        row = res.first()
        
        if not row:
            raise HTTPException(status_code=404, detail="Booking not found")
            
        booking, movie, room, showtime = row
        
        # Get seats
        stmt_seats = (
            select(SeatTable)
            .join(ShowSeatTable, ShowSeatTable.seat_id == SeatTable.seat_id)
            .join(BookingItemTable, BookingItemTable.show_seat_id == ShowSeatTable.show_seat_id)
            .where(BookingItemTable.booking_id == booking.booking_id)
        )
        res_seats = await db.execute(stmt_seats)
        seats = res_seats.scalars().all()
        seat_labels = [f"{s.seat_row}{s.seat_num}" for s in seats]
        
        return {
            "booking_id": booking.booking_id,
            "total_price": booking.total_price,
            "status": booking.status,
            "movie_title": movie.title,
            "room_name": room.name,
            "showtime_start": showtime.start_time.isoformat(),
            "seats": seat_labels
        }

    @staticmethod
    async def get_user_bookings(db: AsyncSession, user_id: int):
        stmt = (
            select(BookingTable, MovieTable, RoomTable, ShowtimeTable)
            .join(ShowtimeTable, ShowtimeTable.showtime_id == BookingTable.showtime_id)
            .join(MovieTable, MovieTable.movie_id == ShowtimeTable.movie_id)
            .join(RoomTable, RoomTable.room_id == ShowtimeTable.room_id)
            .where(BookingTable.customer_id == user_id)
            .order_by(BookingTable.booking_date.desc())
        )
        res = await db.execute(stmt)
        rows = res.all()
        
        results = []
        for booking, movie, room, showtime in rows:
            # Get seats
            stmt_seats = (
                select(SeatTable)
                .join(ShowSeatTable, ShowSeatTable.seat_id == SeatTable.seat_id)
                .join(BookingItemTable, BookingItemTable.show_seat_id == ShowSeatTable.show_seat_id)
                .where(BookingItemTable.booking_id == booking.booking_id)
            )
            res_seats = await db.execute(stmt_seats)
            seats = res_seats.scalars().all()
            seat_labels = [f"{s.seat_row}{s.seat_num}" for s in seats]

            # Get e-ticket QR codes (only for paid bookings)
            qr_codes = []
            if booking.status == "paid":
                stmt_tickets = (
                    select(ETicketTable)
                    .join(BookingItemTable, BookingItemTable.item_id == ETicketTable.item_id)
                    .where(BookingItemTable.booking_id == booking.booking_id)
                )


    @staticmethod
    async def timeout_booking_task(booking_id: int):
        # Wait for 10 minutes
        await asyncio.sleep(600)
        async with AsyncSessionLocal() as db:
            await BookingController.cancel_booking(db, booking_id)

    @staticmethod
    async def cancel_booking(db: AsyncSession, booking_id: int):
        res = await db.execute(select(BookingTable).where(BookingTable.booking_id == booking_id))
        booking = res.scalars().first()
        
        if booking and booking.status == "pending":
            booking.status = "cancelled"
            
            # Release seats
            res_items = await db.execute(select(BookingItemTable).where(BookingItemTable.booking_id == booking_id))
            items = res_items.scalars().all()
            
            for item in items:
                res_ss = await db.execute(select(ShowSeatTable).where(ShowSeatTable.show_seat_id == item.show_seat_id))
                show_seat = res_ss.scalars().first()
                if show_seat:
                    show_seat.status = "Available"
                    show_seat.booking_id = None
                    
            await db.commit()

    @staticmethod
    async def start_background_cleanup_task():
        """
        Background task chạy mỗi 2 phút.
        Tìm các booking 'pending' đã quá hạn 10 phút và tự động huỷ.
        """
        import logging
        logger = logging.getLogger(__name__)
        while True:
            try:
                async with AsyncSessionLocal() as db:
                    # Tính mốc thời gian cách đây 10 phút
                    threshold = datetime.now(timezone.utc) - timedelta(minutes=10)
                    
                    # Tìm các booking pending quá hạn
                    stmt = select(BookingTable).where(
                        BookingTable.status == "pending",
                        BookingTable.booking_date <= threshold
                    )
                    res = await db.execute(stmt)
                    expired_bookings = res.scalars().all()
                    
                    for b in expired_bookings:
                        logger.info(f"Background Sweeper: Đang huỷ đơn hàng quá hạn {b.booking_id}")
                        await BookingController.cancel_booking(db, b.booking_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Lỗi trong Background Sweeper: {e}")
                
            try:
                await asyncio.sleep(120)  # Ngủ 2 phút rồi mới chạy lại
            except asyncio.CancelledError:
                break

    @staticmethod
    async def get_booking_detail(db: AsyncSession, user_id: int, booking_id: int):
        # Join bookings -> showtimes -> movies & rooms
        stmt = (
            select(BookingTable, MovieTable, RoomTable, ShowtimeTable)
            .join(ShowtimeTable, ShowtimeTable.showtime_id == BookingTable.showtime_id)
            .join(MovieTable, MovieTable.movie_id == ShowtimeTable.movie_id)
            .join(RoomTable, RoomTable.room_id == ShowtimeTable.room_id)
            .where(
                BookingTable.booking_id == booking_id,
                BookingTable.customer_id == user_id
            )
        )
        res = await db.execute(stmt)
        row = res.first()
        
        if not row:
            raise HTTPException(status_code=404, detail="Booking not found")
            
        booking, movie, room, showtime = row
        
        # Get seats
        stmt_seats = (
            select(SeatTable)
            .join(ShowSeatTable, ShowSeatTable.seat_id == SeatTable.seat_id)
            .join(BookingItemTable, BookingItemTable.show_seat_id == ShowSeatTable.show_seat_id)
            .where(BookingItemTable.booking_id == booking.booking_id)
        )
        res_seats = await db.execute(stmt_seats)
        seats = res_seats.scalars().all()
        seat_labels = [f"{s.seat_row}{s.seat_num}" for s in seats]
        
        return {
            "booking_id": booking.booking_id,
            "total_price": booking.total_price,
            "status": booking.status,
            "movie_title": movie.title,
            "room_name": room.name,
            "showtime_start": showtime.start_time.isoformat(),
            "seats": seat_labels
        }

    @staticmethod
    async def get_user_bookings(db: AsyncSession, user_id: int):
        stmt = (
            select(BookingTable, MovieTable, RoomTable, ShowtimeTable)
            .join(ShowtimeTable, ShowtimeTable.showtime_id == BookingTable.showtime_id)
            .join(MovieTable, MovieTable.movie_id == ShowtimeTable.movie_id)
            .join(RoomTable, RoomTable.room_id == ShowtimeTable.room_id)
            .where(BookingTable.customer_id == user_id)
            .order_by(BookingTable.booking_date.desc())
        )
        res = await db.execute(stmt)
        rows = res.all()
        
        results = []
        for booking, movie, room, showtime in rows:
            # Get seats
            stmt_seats = (
                select(SeatTable)
                .join(ShowSeatTable, ShowSeatTable.seat_id == SeatTable.seat_id)
                .join(BookingItemTable, BookingItemTable.show_seat_id == ShowSeatTable.show_seat_id)
                .where(BookingItemTable.booking_id == booking.booking_id)
            )
            res_seats = await db.execute(stmt_seats)
            seats = res_seats.scalars().all()
            seat_labels = [f"{s.seat_row}{s.seat_num}" for s in seats]

            # Get e-ticket QR codes (only for paid bookings)
            qr_codes = []
            if booking.status == "paid":
                stmt_tickets = (
                    select(ETicketTable)
                    .join(BookingItemTable, BookingItemTable.item_id == ETicketTable.item_id)
                    .where(BookingItemTable.booking_id == booking.booking_id)
                )
                res_tickets = await db.execute(stmt_tickets)
                tickets = res_tickets.scalars().all()
                qr_codes = [t.qr_code for t in tickets if t.is_valid]
            
            results.append({
                "booking_id": booking.booking_id,
                "total_price": booking.total_price,
                "status": booking.status,
                "movie_title": movie.title,
                "room_name": room.name,
                "showtime_start": showtime.start_time.isoformat(),
                "seats": seat_labels,
                "qr_codes": qr_codes
            })
            
        return results

    @staticmethod
    async def get_admin_bookings(db: AsyncSession, page: int = 1, limit: int = 12, search: str = "", status: str = "all"):
        from src.models.theater import SeatTable, ShowSeatTable
        from src.models.booking import BookingItemTable
        from sqlalchemy import or_, func, cast, String

        base_query = (
            select(BookingTable, MovieTable, RoomTable, ShowtimeTable, UserTable)
            .join(ShowtimeTable, ShowtimeTable.showtime_id == BookingTable.showtime_id)
            .join(MovieTable, MovieTable.movie_id == ShowtimeTable.movie_id)
            .join(RoomTable, RoomTable.room_id == ShowtimeTable.room_id)
            .join(UserTable, UserTable.user_id == BookingTable.customer_id)
        )

        if status != "all":
            # Map frontend statuses to DB statuses if needed, but DB uses 'pending', 'paid', 'cancelled'
            base_query = base_query.where(BookingTable.status == status.lower())

        if search:
            search_pattern = f"%{search.lower()}%"
            base_query = base_query.where(
                or_(
                    func.lower(UserTable.full_name).like(search_pattern),
                    func.lower(UserTable.email).like(search_pattern),
                    func.lower(MovieTable.title).like(search_pattern),
                    cast(BookingTable.booking_id, String).like(search_pattern)
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_res = await db.execute(count_stmt)
        total_items = total_res.scalar_one()

        # Paginate
        stmt = base_query.order_by(BookingTable.booking_date.desc()).offset((page - 1) * limit).limit(limit)
        res = await db.execute(stmt)
        rows = res.all()
        
        results = []
        for booking, movie, room, showtime, user in rows:
            # Get seats for this booking
            stmt_seats = (
                select(SeatTable)
                .join(ShowSeatTable, ShowSeatTable.seat_id == SeatTable.seat_id)
                .join(BookingItemTable, BookingItemTable.show_seat_id == ShowSeatTable.show_seat_id)
                .where(BookingItemTable.booking_id == booking.booking_id)
            )
            res_seats = await db.execute(stmt_seats)
            seats = res_seats.scalars().all()
            seat_labels = [f"{s.seat_row}{s.seat_num}" for s in seats]

            results.append({
                "id": f"#BK-{booking.booking_id:04d}",
                "booking_id": booking.booking_id,
                "customerName": user.full_name,
                "customerEmail": user.email,
                "movieTitle": movie.title,
                "movieGenre": movie.genre,
                "poster": movie.poster_url,
                "amount": booking.total_price,
                "status": booking.status.capitalize(), # "pending" -> "Pending"
                "time": booking.booking_date.strftime("%H:%M - %d/%m/%Y") if booking.booking_date else "",
                "showtime": showtime.start_time.strftime("%H:%M - %d/%m/%Y"),
                "room": room.name,
                "seats": ", ".join(seat_labels),
                "method": "VNPAY" if booking.status == "paid" else "Chưa thanh toán"
            })
            
        return {
            "items": results,
            "total": total_items
        }

    @staticmethod
    async def update_booking_status(db: AsyncSession, booking_id: int, status: str):
        res = await db.execute(select(BookingTable).where(BookingTable.booking_id == booking_id))
        booking = res.scalars().first()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
            
        if status == "cancelled" and booking.status != "cancelled":
            await BookingController.cancel_booking(db, booking_id)
        else:
            booking.status = status
            await db.commit()
            
        return {"message": "Status updated successfully", "status": booking.status}
