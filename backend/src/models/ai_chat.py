# src/models/ai_chat.py
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from src.config.db import Base


# ─────────────────────────────────────────────────────────────────────────────
# 1. SQLALCHEMY TABLES
# ─────────────────────────────────────────────────────────────────────────────

class AIConversationTable(Base):
    """Mỗi phiên hội thoại của một user với chatbot."""
    __tablename__ = "ai_conversations"

    conversation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationship: 1 conversation → nhiều messages (xóa conversation → xóa messages)
    messages: Mapped[List["AIMessageTable"]] = relationship(
        "AIMessageTable",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="AIMessageTable.sent_at",
    )


class AIMessageTable(Base):
    """Từng tin nhắn trong một phiên hội thoại."""
    __tablename__ = "ai_messages"

    message_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("ai_conversations.conversation_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_type: Mapped[str] = mapped_column(Text, nullable=False)  # "user" | "ai"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    conversation: Mapped["AIConversationTable"] = relationship(
        "AIConversationTable", back_populates="messages"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2. PYDANTIC SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────

class ChatHistoryItem(BaseModel):
    """Một cặp tin nhắn trong lịch sử hội thoại."""
    role: str       # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    """Schema nhận từ frontend khi user gửi tin nhắn."""
    message: str
    history: List[ChatHistoryItem] = []
    conversation_id: Optional[int] = None  # None = tạo phiên mới


class SuggestedMovie(BaseModel):
    """Thông tin phim được gợi ý trong phản hồi AI."""
    movie_id: int
    title: str
    poster_url: str
    genre: str


class ChatResponse(BaseModel):
    """Schema trả về cho frontend."""
    reply: str
    suggested_movies: List[SuggestedMovie] = []
    conversation_id: Optional[int] = None  # None nếu là Guest


class MessageResponse(BaseModel):
    """Một tin nhắn trong lịch sử."""
    message_id: int
    sender_type: str
    content: str
    sent_at: datetime

    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    """Tóm tắt một phiên hội thoại (dùng cho GET /ai/conversations)."""
    conversation_id: int
    started_at: datetime
    preview: Optional[str] = None   # Câu hỏi đầu tiên của user
    message_count: int = 0

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    """Chi tiết một phiên hội thoại kèm toàn bộ tin nhắn."""
    conversation_id: int
    started_at: datetime
    messages: List[MessageResponse]

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Danh sách phiên hội thoại của user."""
    conversations: List[ConversationSummary]
