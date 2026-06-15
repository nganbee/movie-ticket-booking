# src/routes/ai.py
"""
AI Chatbot Router – 6 endpoints:
  POST   /ai/chat
  GET    /ai/conversations
  GET    /ai/conversations/{id}/messages
  DELETE /ai/conversations/{id}
  GET    /ai/status
  POST   /ai/rebuild-index
"""

from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.db import get_db
from src.middlewares.auth import get_current_user, verify_admin
from src.models.user import UserTable
from src.models.ai_chat import (
    ChatRequest,
    ChatResponse,
    ConversationListResponse,
    ConversationDetailResponse,
)
from src.controllers.ai_controller import AIController

router = APIRouter()

# Bearer scheme tuỳ chọn (optional auth) – dùng cho /ai/chat
_optional_bearer = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer),
    db: AsyncSession = Depends(get_db),
) -> Optional[UserTable]:
    """
    Dependency: Trả về UserTable nếu có JWT hợp lệ, None nếu là Guest.
    Không raise lỗi khi không có token.
    """
    if credentials is None:
        return None
    from src.services.auth_service import AuthService
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    if payload is None:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        return None
    return await AuthService.get_user_by_id(db, int(user_id))


# ─────────────────────────────────────────────────────────────────────────────
# 1. POST /ai/chat – Public (Guest OK, JWT → lưu lịch sử)
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserTable] = Depends(get_optional_user),
):
    """
    Gửi tin nhắn đến AI, nhận phản hồi kèm danh sách phim gợi ý.
    - Guest: không cần JWT, không lưu lịch sử.
    - User đã đăng nhập: truyền Bearer token, lịch sử được lưu vào DB.
    """
    return await AIController.chat(req, db, current_user)


# ─────────────────────────────────────────────────────────────────────────────
# 2. GET /ai/conversations – JWT Required
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: UserTable = Depends(get_current_user),
):
    """Lấy danh sách tất cả phiên chat của user đang đăng nhập."""
    return await AIController.get_conversations(current_user, db)


# ─────────────────────────────────────────────────────────────────────────────
# 3. GET /ai/conversations/{id}/messages – JWT Required
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/conversations/{conversation_id}/messages", response_model=ConversationDetailResponse)
async def get_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserTable = Depends(get_current_user),
):
    """Lấy toàn bộ tin nhắn trong một phiên chat. Chỉ trả về phiên thuộc về user."""
    return await AIController.get_messages(conversation_id, current_user, db)


# ─────────────────────────────────────────────────────────────────────────────
# 4. DELETE /ai/conversations/{id} – JWT Required
# ─────────────────────────────────────────────────────────────────────────────
@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserTable = Depends(get_current_user),
):
    """Xóa một phiên chat và toàn bộ tin nhắn trong đó."""
    await AIController.delete_conversation(conversation_id, current_user, db)


# ─────────────────────────────────────────────────────────────────────────────
# 5. GET /ai/status – Public
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/status")
async def get_status():
    """Kiểm tra trạng thái Ollama và FAISS index. Dùng cho frontend hiển thị badge."""
    return await AIController.get_status()


# ─────────────────────────────────────────────────────────────────────────────
# 6. POST /ai/rebuild-index – Admin Only
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/rebuild-index", dependencies=[Depends(verify_admin)])
async def rebuild_index(db: AsyncSession = Depends(get_db)):
    """
    Rebuild FAISS index từ dữ liệu phim hiện tại trong DB.
    Gọi sau khi admin thêm phim mới hoặc cập nhật suất chiếu.
    """
    return await AIController.rebuild_index(db)
