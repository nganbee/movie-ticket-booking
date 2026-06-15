# src/services/ai_service.py
"""
RAG Pipeline cho CineBook Chatbot.

Luồng:
  1. load_movie_documents(db)     → Query PostgreSQL → List[Document]
  2. build_or_load_vectorstore()  → FAISS index (lazy-init, cached in memory)
  3. build_rag_chain(vectorstore) → LCEL chain (retriever | prompt | llm | parser)
  4. chat(request, db)            → Gọi chain, lưu DB nếu có user, trả kết quả

LLM      : Groq API – llama-3.3-70b-versatile  (~500 tokens/s, cloud)
Embedding: HuggingFace – paraphrase-multilingual-MiniLM-L12-v2 (local, hỗ trợ tiếng Việt)
"""

import os
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from src.config.settings import settings
from src.models.movie import MovieTable
from src.models.theater import ShowtimeTable, RoomTable, TheaterTable

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Global cache – chỉ khởi tạo 1 lần, dùng lại cho mọi request
# ─────────────────────────────────────────────────────────────────────────────
_vectorstore: Optional[FAISS] = None
_embedding_model: Optional[HuggingFaceEmbeddings] = None
_llm: Optional[ChatGroq] = None


def _get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Lazy-init HuggingFaceEmbeddings.
    Lần đầu gọi sẽ tải model ~90MB về máy (chỉ 1 lần).
    Các lần sau dùng lại từ cache.
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name=settings.EMBED_MODEL,
            model_kwargs={"device": "cpu"},   # dùng CPU, không cần GPU
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info(f"[AI] Embedding model loaded: {settings.EMBED_MODEL}")
    return _embedding_model


def _get_llm() -> ChatGroq:
    """
    Lazy-init ChatGroq.
    Groq chạy trên cloud, tốc độ ~300-800 tokens/s – không cần timeout lớn.
    """
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.7,
            max_tokens=512,          # Groq nhanh nên có thể để cao hơn Ollama
        )
        logger.info(f"[AI] Groq LLM initialized: {settings.GROQ_MODEL}")
    return _llm


# ─────────────────────────────────────────────────────────────────────────────
# Bước 1: Load dữ liệu từ PostgreSQL → List[Document]
# ─────────────────────────────────────────────────────────────────────────────

def _genre_to_mood(genre: str) -> str:
    """Ánh xạ thể loại phim → từ khoá tâm trạng phù hợp."""
    mapping = {
        "hành động":    "hào hứng, kịch tính, mạo hiểm, phấn khích",
        "hài":          "vui, cười, chill, thư giãn, nhẹ nhàng",
        "tình cảm":     "lãng mạn, nhớ người yêu, muốn khóc, cảm xúc",
        "kinh dị":      "hồi hộp, sợ, mạo hiểm, kịch tính",
        "hoạt hình":    "vui, gia đình, trẻ em, chill",
        "gia đình":     "ấm áp, gia đình, vui, cảm xúc",
        "tâm lý":       "suy nghĩ, triết lý, trầm, tĩnh tâm",
        "viễn tưởng":   "mạo hiểm, kỳ diệu, sáng tạo",
        "khoa học":     "mạo hiểm, kỳ diệu, sáng tạo",
        "chiến tranh":  "hào hùng, cảm động, kịch tính",
        "tài liệu":     "học hỏi, tĩnh tâm, suy nghĩ",
        "phiêu lưu":    "hào hứng, mạo hiểm, kịch tính",
        "âm nhạc":      "vui, chill, cảm xúc, thư giãn",
        "thể thao":     "hào hứng, cảm hứng, động lực",
    }
    tags = []
    genre_lower = genre.lower()
    for key, val in mapping.items():
        if key in genre_lower:
            tags.append(val)
    return ", ".join(tags) if tags else "giải trí chung"


async def load_movie_documents(db: AsyncSession) -> list[Document]:
    """
    Query phim đang chiếu từ PostgreSQL, gộp suất chiếu theo phim,
    chuyển thành List[Document] cho FAISS.
    """
    stmt = (
        select(
            MovieTable.movie_id,
            MovieTable.title,
            MovieTable.genre,
            MovieTable.description,
            MovieTable.director,
            MovieTable.language,
            MovieTable.duration,
            MovieTable.status,
            MovieTable.imdb_rating,
            MovieTable.poster_url,
            func.string_agg(
                func.to_char(ShowtimeTable.start_time, "HH24:MI DD/MM")
                + " tại "
                + TheaterTable.name
                + " ("
                + RoomTable.name
                + " - "
                + ShowtimeTable.format
                + ")",
                text("', '"),
            ).label("showtime_info"),
        )
        .outerjoin(ShowtimeTable, ShowtimeTable.movie_id == MovieTable.movie_id)
        .outerjoin(RoomTable, RoomTable.room_id == ShowtimeTable.room_id)
        .outerjoin(TheaterTable, TheaterTable.theater_id == RoomTable.theater_id)
        .where(MovieTable.status == "now_showing")
        .group_by(
            MovieTable.movie_id,
            MovieTable.title,
            MovieTable.genre,
            MovieTable.description,
            MovieTable.director,
            MovieTable.language,
            MovieTable.duration,
            MovieTable.status,
            MovieTable.imdb_rating,
            MovieTable.poster_url,
        )
    )

    result = await db.execute(stmt)
    rows = result.all()

    documents: list[Document] = []
    for row in rows:
        mood_tags = _genre_to_mood(row.genre)
        imdb_str = f"{row.imdb_rating}/10" if row.imdb_rating else "Chưa có"
        showtime_str = row.showtime_info if row.showtime_info else "Chưa có lịch chiếu"

        page_content = (
            f"Tên phim: {row.title}\n"
            f"Thể loại: {row.genre}\n"
            f"Đạo diễn: {row.director}\n"
            f"Ngôn ngữ: {row.language}\n"
            f"Thời lượng: {row.duration} phút\n"
            f"IMDb: {imdb_str}\n"
            f"Trạng thái: Đang chiếu\n"
            f"Nội dung: {row.description}\n"
            f"Suất chiếu: {showtime_str}\n"
            f"Tâm trạng phù hợp: {mood_tags}"
        )

        doc = Document(
            page_content=page_content,
            metadata={
                "movie_id":   row.movie_id,
                "title":      row.title,
                "genre":      row.genre,
                "poster_url": row.poster_url or "",
                "status":     row.status,
            },
        )
        documents.append(doc)

    logger.info(f"[AI] Loaded {len(documents)} movie documents from DB.")
    return documents


# ─────────────────────────────────────────────────────────────────────────────
# Bước 2: Build / Load FAISS vectorstore
# ─────────────────────────────────────────────────────────────────────────────

async def build_vectorstore(db: AsyncSession) -> FAISS:
    """Build FAISS index từ DB và lưu xuống disk."""
    documents = await load_movie_documents(db)
    if not documents:
        raise ValueError("Không có phim nào đang chiếu để tạo index.")

    embed = _get_embedding_model()
    vs = FAISS.from_documents(documents, embed)
    vs.save_local(settings.FAISS_INDEX_PATH)
    logger.info(f"[AI] FAISS index built: {len(documents)} documents.")
    return vs


async def get_vectorstore(db: AsyncSession) -> FAISS:
    """
    Lazy-init: load từ disk nếu đã có, ngược lại build mới.
    Kết quả được cache trong biến global để tái dùng.
    """
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    embed = _get_embedding_model()
    idx_file = os.path.join(settings.FAISS_INDEX_PATH, "index.faiss")

    if os.path.exists(idx_file):
        _vectorstore = FAISS.load_local(
            settings.FAISS_INDEX_PATH,
            embed,
            allow_dangerous_deserialization=True,
        )
        logger.info("[AI] FAISS index loaded from disk.")
    else:
        _vectorstore = await build_vectorstore(db)

    return _vectorstore


async def rebuild_vectorstore(db: AsyncSession) -> tuple[FAISS, int]:
    """Rebuild index (gọi khi admin thêm phim mới). Trả về (vectorstore, số doc)."""
    global _vectorstore
    vs = await build_vectorstore(db)
    _vectorstore = vs
    return vs, vs.index.ntotal


# ─────────────────────────────────────────────────────────────────────────────
# Bước 3: Prompt template + LCEL Chain
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM_TEMPLATE = """Bạn là trợ lý ảo CineBook – hệ thống đặt vé xem phim trực tuyến tại TP.HCM.

NHIỆM VỤ CHÍNH:
- Gợi ý phim phù hợp dựa trên TÂM TRẠNG, sở thích, và hoàn cảnh của người dùng.
- Cung cấp thông tin lịch chiếu, địa điểm rạp chính xác.
- Hỗ trợ hướng dẫn đặt vé trên website CineBook.

NGUYÊN TẮC BẮT BUỘC:
1. Chỉ gợi ý phim CÓ TRONG danh sách [DỮ LIỆU PHIM] bên dưới. KHÔNG tự bịa phim.
2. Nếu không có phim phù hợp, thành thật nói: "Hiện tại CineBook chưa có phim phù hợp với yêu cầu của bạn."
3. Luôn trả lời bằng TIẾNG VIỆT, thân thiện, gần gũi.
4. Khi gợi ý phim, luôn kèm: tên phim, thể loại, và suất chiếu gần nhất.
5. Nếu người dùng hỏi ngoài chủ đề phim/rạp chiếu, nhẹ nhàng hướng về chủ đề chính.

[DỮ LIỆU PHIM ĐANG CHIẾU TẠI CINEBOOK]:
{context}"""

_prompt = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_TEMPLATE),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])


def _format_docs(docs: list[Document]) -> str:
    """Nối nội dung các Document thành 1 chuỗi context."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def _build_rag_chain(vectorstore: FAISS):
    """
    Xây dựng LCEL chain:
      {question, chat_history}
        → retrieve top-4 docs theo question
        → format thành context string
        → prompt template
        → Groq LLM
        → parse thành string
    """
    from operator import itemgetter

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4},
    )
    llm = _get_llm()

    chain = (
        {
            "context":      itemgetter("question") | retriever | _format_docs,
            "question":     itemgetter("question"),
            "chat_history": itemgetter("chat_history"),
        }
        | _prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever


# ─────────────────────────────────────────────────────────────────────────────
# Public interface: hàm chat() gọi từ controller
# ─────────────────────────────────────────────────────────────────────────────

async def chat(
    message: str,
    history: list[dict],      # [{"role": "user"|"assistant", "content": "..."}]
    db: AsyncSession,
) -> dict:
    """
    Thực hiện RAG pipeline:
    1. Lấy vectorstore (lazy load)
    2. Retrieve top-4 phim liên quan
    3. Gọi Groq LLM với context + history
    4. Trả về reply + suggested_movies
    """
    vectorstore = await get_vectorstore(db)
    chain, retriever = _build_rag_chain(vectorstore)

    # Chuyển history sang LangChain message format
    chat_history = []
    for msg in history[-12:]:   # Giữ tối đa 6 cặp = 12 entries
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=msg["content"]))

    # Invoke chain (async)
    reply: str = await chain.ainvoke({
        "question":     message,
        "chat_history": chat_history,
    })

    # Lấy danh sách phim được retrieve (để trả suggested_movies)
    retrieved_docs: list[Document] = retriever.invoke(message)
    suggested_movies = [
        {
            "movie_id":   doc.metadata["movie_id"],
            "title":      doc.metadata["title"],
            "poster_url": doc.metadata["poster_url"],
            "genre":      doc.metadata["genre"],
        }
        for doc in retrieved_docs
    ]

    return {
        "reply":            reply,
        "suggested_movies": suggested_movies,
    }


async def check_ai_status() -> dict:
    """Kiểm tra Groq API có kết nối được không bằng cách gọi thử một request nhỏ."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            )
            resp.raise_for_status()
        index_size = _vectorstore.index.ntotal if _vectorstore else 0
        return {
            "status":     "online",
            "llm":        settings.GROQ_MODEL,
            "embedding":  settings.EMBED_MODEL,
            "index_size": index_size,
            "message":    "AI service is ready (Groq + HuggingFace).",
        }
    except Exception as e:
        return {
            "status":  "offline",
            "message": f"Groq API unreachable: {e}",
        }
