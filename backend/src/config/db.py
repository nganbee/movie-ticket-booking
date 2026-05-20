# src/config/db.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_URL")

# 1. Tạo Engine kết nối bất đồng bộ tới Supabase
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# 2. Tạo Session factory để sinh ra các phiên làm việc với DB
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Base class để các Models kế thừa và định nghĩa bảng
class Base(DeclarativeBase):
    pass

# 4. Dependency cung cấp Session cho các request (Dùng trong Route/Controller)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()