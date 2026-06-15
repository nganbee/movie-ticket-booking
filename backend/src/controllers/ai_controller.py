# src/controllers/ai_controller.py
"""
Controller cho AI Chatbot – xử lý logic HTTP cho 6 endpoints:
  1. POST /ai/chat
  2. GET  /ai/conversations
  3. GET  /ai/conversations/{id}/messages
  4. DELETE /ai/conversations/{id}
  5. GET  /ai/status
  6. POST /ai/rebuild-index
"""

import time
import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from src.models.ai_chat import (
    AIConversationTable,
    AIMessageTable,
    ChatRequest,
    ChatResponse,
    SuggestedMovie,
    ConversationSummary,
    ConversationListResponse,
    ConversationDetailResponse,
    MessageResponse,
)
from src.models.user import UserTable
from src.services import ai_service

logger = logging.getLogger(__name__)


class AIController:

    # ─────────────────────────────────────────────────────────────────────────
    # 1. POST /ai/chat
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    async def chat(
        req: ChatRequest,
        db: AsyncSession,
        current_user: UserTable | None,  # None = Guest
    ) -> ChatResponse:
        """
        Gọi RAG pipeline, lưu tin nhắn vào DB nếu user đã đăng nhập.
        Guest vẫn nhận được phản hồi nhưng không lưu lịch sử.
        """
        # Chuyển history sang dict list cho service
        history_dicts = [
            {"role": item.role, "content": item.content}
            for item in req.history
        ]

        try:
            result = await ai_service.chat(
                message=req.message,
                history=history_dicts,
                db=db,
            )
        except Exception as e:
            logger.error(f"[AI] RAG chain error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service hiện không khả dụng. Vui lòng thử lại sau.",
            )

        conversation_id: int | None = None

        # Lưu vào DB chỉ khi user đã đăng nhập
        if current_user is not None:
            now = datetime.now(timezone.utc)

            # Tạo phiên mới hoặc dùng phiên đã có
            if req.conversation_id is None:
                conversation = AIConversationTable(
                    customer_id=current_user.user_id,
                    started_at=now,
                )
                db.add(conversation)
                await db.flush()          # Lấy conversation_id do DB sinh ra
                conversation_id = conversation.conversation_id
            else:
                # Kiểm tra phiên tồn tại và thuộc về user này
                conv_result = await db.execute(
                    select(AIConversationTable).where(
                        AIConversationTable.conversation_id == req.conversation_id,
                        AIConversationTable.customer_id == current_user.user_id,
                    )
                )
                conversation = conv_result.scalar_one_or_none()
                if conversation is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Không tìm thấy phiên chat này.",
                    )
                conversation_id = conversation.conversation_id

            # Lưu tin nhắn user
            db.add(AIMessageTable(
                conversation_id=conversation_id,
                sender_type="user",
                content=req.message,
                sent_at=now,
            ))
            # Lưu phản hồi AI
            db.add(AIMessageTable(
                conversation_id=conversation_id,
                sender_type="ai",
                content=result["reply"],
                sent_at=now,
            ))
            # Commit được xử lý bởi get_db() dependency

        return ChatResponse(
            reply=result["reply"],
            suggested_movies=[
                SuggestedMovie(**m) for m in result["suggested_movies"]
            ],
            conversation_id=conversation_id,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 2. GET /ai/conversations
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    async def get_conversations(
        current_user: UserTable,
        db: AsyncSession,
    ) -> ConversationListResponse:
        """Lấy danh sách phiên chat của user, kèm preview và số lượng tin nhắn."""

        # Sub-query: lấy tin nhắn đầu tiên của user trong mỗi phiên (preview)
        first_msg_subq = (
            select(
                AIMessageTable.conversation_id,
                AIMessageTable.content.label("preview"),
            )
            .where(AIMessageTable.sender_type == "user")
            .distinct(AIMessageTable.conversation_id)
            .order_by(
                AIMessageTable.conversation_id,
                AIMessageTable.sent_at.asc(),
            )
            .subquery()
        )

        # Query chính: conversations + preview + message_count
        stmt = (
            select(
                AIConversationTable.conversation_id,
                AIConversationTable.started_at,
                first_msg_subq.c.preview,
                func.count(AIMessageTable.message_id).label("message_count"),
            )
            .outerjoin(
                AIMessageTable,
                AIMessageTable.conversation_id == AIConversationTable.conversation_id,
            )
            .outerjoin(
                first_msg_subq,
                first_msg_subq.c.conversation_id == AIConversationTable.conversation_id,
            )
            .where(AIConversationTable.customer_id == current_user.user_id)
            .group_by(
                AIConversationTable.conversation_id,
                AIConversationTable.started_at,
                first_msg_subq.c.preview,
            )
            .order_by(AIConversationTable.started_at.desc())
        )

        result = await db.execute(stmt)
        rows = result.all()

        conversations = [
            ConversationSummary(
                conversation_id=row.conversation_id,
                started_at=row.started_at,
                preview=row.preview,
                message_count=row.message_count or 0,
            )
            for row in rows
        ]
        return ConversationListResponse(conversations=conversations)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. GET /ai/conversations/{id}/messages
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    async def get_messages(
        conversation_id: int,
        current_user: UserTable,
        db: AsyncSession,
    ) -> ConversationDetailResponse:
        """Lấy toàn bộ tin nhắn trong một phiên, kiểm tra ownership."""

        # Kiểm tra phiên tồn tại và thuộc user này
        conv_result = await db.execute(
            select(AIConversationTable).where(
                AIConversationTable.conversation_id == conversation_id,
                AIConversationTable.customer_id == current_user.user_id,
            )
        )
        conversation = conv_result.scalar_one_or_none()
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phiên chat này.",
            )

        # Lấy tất cả tin nhắn theo thứ tự thời gian
        msg_result = await db.execute(
            select(AIMessageTable)
            .where(AIMessageTable.conversation_id == conversation_id)
            .order_by(AIMessageTable.sent_at.asc())
        )
        messages = msg_result.scalars().all()

        return ConversationDetailResponse(
            conversation_id=conversation.conversation_id,
            started_at=conversation.started_at,
            messages=[MessageResponse.model_validate(m) for m in messages],
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 4. DELETE /ai/conversations/{id}
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    async def delete_conversation(
        conversation_id: int,
        current_user: UserTable,
        db: AsyncSession,
    ) -> None:
        """Xóa phiên chat và toàn bộ tin nhắn (ON DELETE CASCADE xử lý messages)."""

        conv_result = await db.execute(
            select(AIConversationTable).where(
                AIConversationTable.conversation_id == conversation_id,
                AIConversationTable.customer_id == current_user.user_id,
            )
        )
        conversation = conv_result.scalar_one_or_none()
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phiên chat này.",
            )

        await db.delete(conversation)
        # Commit được xử lý bởi get_db() dependency
        return None

    # ─────────────────────────────────────────────────────────────────────────
    # 5. GET /ai/status
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    async def get_status() -> dict:
        """Health check: kiểm tra Groq API kết nối được và FAISS index sẵn sàng."""
        status_info = await ai_service.check_ai_status()
        if status_info["status"] == "offline":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=status_info,
            )
        return status_info

    # ─────────────────────────────────────────────────────────────────────────
    # 6. POST /ai/rebuild-index (Admin only)
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    async def rebuild_index(
        db: AsyncSession,
    ) -> dict:
        """Rebuild FAISS index từ DB. Gọi sau khi admin thêm/cập nhật phim."""
        t0 = time.perf_counter()
        try:
            _, doc_count = await ai_service.rebuild_vectorstore(db)
        except Exception as e:
            logger.error(f"[AI] Rebuild index error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Rebuild thất bại: {str(e)}",
            )
        elapsed = round(time.perf_counter() - t0, 2)
        return {
            "message":            "FAISS index rebuilt successfully.",
            "documents_indexed":  doc_count,
            "time_taken_seconds": elapsed,
        }
