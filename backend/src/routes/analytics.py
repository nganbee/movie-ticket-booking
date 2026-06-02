# src/routes/analytics.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import Optional
from datetime import datetime, date, timedelta

from src.config.db import get_db
from src.middlewares.auth import verify_admin
from src.models.booking import BookingTable, BookingItemTable
from src.models.theater import ShowtimeTable
from src.models.movie import MovieTable
from src.models.user import UserTable

router = APIRouter()


@router.get("/dashboard", dependencies=[Depends(verify_admin)])
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """
    Trả về toàn bộ dữ liệu cho trang Dashboard admin:
    - KPI tổng quan (doanh thu, số vé, số đặt vé, giá vé TB)
    - Top 5 phim bán chạy nhất
    - 10 đặt vé gần nhất
    - Doanh thu theo tháng trong năm hiện tại
    """

    # ── 1. KPI TỔNG QUAN ────────────────────────────────────────────────────────
    # Chỉ tính booking có status = 'paid'
    kpi_stmt = select(
        func.coalesce(func.sum(BookingTable.total_price), 0).label("total_revenue"),
        func.count(BookingTable.booking_id).label("total_bookings"),
    ).where(BookingTable.status == "paid")
    kpi_result = await db.execute(kpi_stmt)
    kpi_row = kpi_result.one()

    # Số vé = tổng số booking_items thuộc các booking đã paid
    tickets_stmt = (
        select(func.count(BookingItemTable.item_id))
        .join(BookingTable, BookingItemTable.booking_id == BookingTable.booking_id)
        .where(BookingTable.status == "paid")
    )
    tickets_result = await db.execute(tickets_stmt)
    total_tickets = tickets_result.scalar_one()

    total_revenue   = int(kpi_row.total_revenue)
    total_bookings  = kpi_row.total_bookings
    avg_ticket_price = round(total_revenue / total_tickets) if total_tickets > 0 else 0

    # ── 2. TOP 5 PHIM BÁN CHẠY ──────────────────────────────────────────────────
    # JOIN: booking_items → bookings → showtimes → movies
    top_movies_stmt = (
        select(
            MovieTable.movie_id,
            MovieTable.title,
            MovieTable.genre,
            MovieTable.poster_url,
            func.count(BookingItemTable.item_id).label("tickets_sold"),
            func.coalesce(func.sum(BookingTable.total_price), 0).label("revenue"),
        )
        .join(ShowtimeTable, ShowtimeTable.movie_id == MovieTable.movie_id)
        .join(BookingTable,  BookingTable.showtime_id == ShowtimeTable.showtime_id)
        .join(BookingItemTable, BookingItemTable.booking_id == BookingTable.booking_id)
        .where(BookingTable.status == "paid")
        .group_by(MovieTable.movie_id, MovieTable.title, MovieTable.genre, MovieTable.poster_url)
        .order_by(func.count(BookingItemTable.item_id).desc())
        .limit(5)
    )
    top_result = await db.execute(top_movies_stmt)
    top_movies = [
        {
            "movie_id":    row.movie_id,
            "title":       row.title,
            "genre":       row.genre,
            "poster":      row.poster_url or "",
            "tickets":     row.tickets_sold,
            "revenue":     int(row.revenue),
        }
        for row in top_result.all()
    ]

    # ── 3. 10 ĐẶT VÉ GẦN NHẤT ──────────────────────────────────────────────────
    recent_stmt = (
        select(
            BookingTable.booking_id,
            BookingTable.total_price,
            BookingTable.status,
            BookingTable.booking_date,
            UserTable.full_name.label("customer"),
            MovieTable.title.label("movie_title"),
        )
        .join(UserTable,     UserTable.user_id == BookingTable.customer_id)
        .join(ShowtimeTable, ShowtimeTable.showtime_id == BookingTable.showtime_id)
        .join(MovieTable,    MovieTable.movie_id == ShowtimeTable.movie_id)
        .order_by(BookingTable.booking_date.desc())
        .limit(10)
    )
    recent_result = await db.execute(recent_stmt)
    recent_bookings = [
        {
            "id":       f"#BK-{row.booking_id:04d}",
            "customer": row.customer,
            "movie":    row.movie_title,
            "amount":   int(row.total_price),
            "status":   row.status,      # pending | paid | cancelled
            "date":     row.booking_date.isoformat() if row.booking_date else None,
        }
        for row in recent_result.all()
    ]

    # ── 4. DOANH THU THEO THÁNG (năm hiện tại) ───────────────────────────────────
    current_year = datetime.now().year
    monthly_stmt = (
        select(
            func.extract("month", BookingTable.booking_date).label("month"),
            func.coalesce(func.sum(BookingTable.total_price), 0).label("revenue"),
        )
        .where(
            BookingTable.status == "paid",
            func.extract("year", BookingTable.booking_date) == current_year,
        )
        .group_by(func.extract("month", BookingTable.booking_date))
        .order_by(func.extract("month", BookingTable.booking_date))
    )
    monthly_result = await db.execute(monthly_stmt)
    monthly_map = {int(row.month): int(row.revenue) // 1_000_000 for row in monthly_result.all()}
    # Đảm bảo đủ 12 tháng, tháng không có dữ liệu = 0
    revenue_by_month = [monthly_map.get(m, 0) for m in range(1, 13)]

    # ── 5. DOANH THU THEO NGÀY (7 ngày gần nhất) ─────────────────────────────────
    today = date.today()
    day_labels = [(today - timedelta(days=6 - i)) for i in range(7)]
    daily_stmt = (
        select(
            func.date(BookingTable.booking_date).label("day"),
            func.coalesce(func.sum(BookingTable.total_price), 0).label("revenue"),
        )
        .where(
            BookingTable.status == "paid",
            func.date(BookingTable.booking_date) >= day_labels[0],
            func.date(BookingTable.booking_date) <= day_labels[-1],
        )
        .group_by(func.date(BookingTable.booking_date))
    )
    daily_result = await db.execute(daily_stmt)
    daily_map = {str(row.day): int(row.revenue) // 1_000_000 for row in daily_result.all()}
    revenue_by_day = [daily_map.get(str(d), 0) for d in day_labels]
    day_label_strings = [d.strftime("%d/%m") for d in day_labels]

    return {
        "kpi": {
            "total_revenue":    total_revenue,
            "total_tickets":    total_tickets,
            "total_bookings":   total_bookings,
            "avg_ticket_price": avg_ticket_price,
        },
        "top_movies":        top_movies,
        "recent_bookings":   recent_bookings,
        "revenue_by_month":  revenue_by_month,
        "revenue_by_day":    revenue_by_day,
        "day_labels":        day_label_strings,
    }
