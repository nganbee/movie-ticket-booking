from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config.db import engine, Base

# Phải import tất cả Table models để SQLAlchemy nhận diện và tạo bảng
from src.models.movie import MovieTable
from src.models.news import NewsTable
from src.models.user import UserTable  # Auth & User tables
from src.models.theater import TheaterTable, RoomTable, SeatTable, ShowtimeTable, ShowSeatTable, PricingRuleTable
from src.models.booking import BookingTable, PaymentTable, BookingItemTable, ETicketTable

from src.routes import movies, news, auth, users, seats, bookings, payments

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khi ứng dụng chạy: Tự động quét Models và tạo bảng trên Supabase nếu chưa tồn tại
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Ket noi Supabase on dinh va dong bo bang thanh cong!")
    yield
    # Khi ứng dụng tắt
    await engine.dispose()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    lifespan=lifespan,
    title="CineBook API",
    version="1.0.0",
    description="Backend API cho hệ thống đặt vé xem phim CineBook",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# ── Public / Auth routes ──────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

# ── User routes (yêu cầu JWT) ─────────────────────────────────────────────────
app.include_router(users.router, prefix="/user", tags=["User"])

# ── Movie & News routes ───────────────────────────────────────────────────────
app.include_router(movies.router, prefix="/movies", tags=["Movies"])
app.include_router(news.router, prefix="/news", tags=["News"])

# ── Booking & Seats routes ────────────────────────────────────────────────────
app.include_router(seats.router, prefix="/seats", tags=["Seats"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])