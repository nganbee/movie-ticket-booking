from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config.db import engine, Base

# Phải import tất cả Table models để SQLAlchemy nhận diện và tạo bảng
from src.models.movie import MovieTable
from src.models.news import MovieNewsTable, PromotionTable, UserNotificationTable
from src.models.user import UserTable  # Auth & User tables
from src.models.theater import TheaterTable, RoomTable, SeatTable, ShowtimeTable, ShowSeatTable, PricingRuleTable
from src.models.booking import BookingTable, PaymentTable, BookingItemTable, ETicketTable
from src.models.ai_chat import AIConversationTable, AIMessageTable  # AI tables
from src.models.showtime import ShowtimeTable, RoomTable, TheaterTable  # Showtime tables
from src.routes import movies, news, auth, users, seats, bookings, payments, showtimes, theaters
from src.routes import analytics
from src.routes import ai as ai_router

from src.config.settings import settings
import ngrok

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khi ứng dụng chạy: Tự động quét Models và tạo bảng trên Supabase nếu chưa tồn tại
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Connected Supabase successfully!")
    
    # Khởi tạo Ngrok tunnel
    if settings.NGROK_AUTHTOKEN:
        try:
            listener = await ngrok.forward(
                "localhost:8000", 
                authtoken=settings.NGROK_AUTHTOKEN,
                domain="gush-unafraid-regain.ngrok-free.dev",
                response_header_add=["ngrok-skip-browser-warning: true"]
            )
            print(f"Ngrok tunnel opened at: {listener.url()}")
        except Exception as e:
            print(f"[WARNING] Ngrok init failed: {e}")
            
    # Bật Background Sweeper dọn dẹp ghế quá hạn
    import asyncio
    from src.controllers.booking_controller import BookingController
    cleanup_task = asyncio.create_task(BookingController.start_background_cleanup_task())
            
    yield
    # Khi ứng dụng tắt
    cleanup_task.cancel()
    await engine.dispose()
    if settings.NGROK_AUTHTOKEN:
        ngrok.disconnect()

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
app.include_router(showtimes.router, prefix="/showtimes", tags=["Showtimes"])
# ── Showtime routes ───────────────────────────────────────────────────────────
app.include_router(showtimes.router, prefix="/showtimes", tags=["Showtimes"])
# ── Analytics routes ──────────────────────────────────────────────────────────
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# ── Theaters routes ──────────────────────────────────────────────────────────
app.include_router(theaters.router, prefix="/theaters", tags=["Theaters"])

# ── AI Chatbot routes ─────────────────────────────────────────────────────────
app.include_router(ai_router.router, prefix="/ai", tags=["AI Chatbot"])
