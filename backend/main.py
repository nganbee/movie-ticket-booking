from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.config.db import engine, Base
from src.models.movie import MovieTable  # Phải import các Table vào để SQLAlchemy nhận diện
from src.models.news import NewsTable
from src.routes import movies, news

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khi ứng dụng chạy: Tự động quét Models và tạo bảng trên Supabase nếu chưa tồn tại
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Ket noi Supabase on dinh va dong bo bang thanh cong!")
    yield
    # Khi ứng dụng tắt
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(movies.router, prefix="/movies", tags=["Movies"])
app.include_router(news.router, prefix="/news", tags=["News"])