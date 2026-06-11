# src/routes/movies.py
from fastapi import APIRouter, Query, Depends, status
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from src.models.movie import MovieResponse, MovieCreate
from src.controllers.movie_controller import MovieController
from src.config.db import get_db
from src.middlewares.auth import verify_admin
from src.services.movie_sync_service import MovieSyncService
from fastapi import HTTPException

router = APIRouter()

# --- Schema phân trang ---
class MoviePageResponse(BaseModel):
    items: List[MovieResponse]
    total: int
    page: int
    limit: int
    total_pages: int

    class Config:
        from_attributes = True

# --- PUBLIC ENDPOINTS ---

@router.get("/", response_model=MoviePageResponse)
async def get_movies(
    status: Optional[str] = Query(None, description="now_showing hoặc coming_soon"),
    genre: Optional[str] = Query(None, description="Thể loại phim"),
    page: int = Query(1, ge=1, description="Số trang (bắt đầu từ 1)"),
    limit: int = Query(12, ge=1, le=100, description="Số phim mỗi trang (tối đa 100)"),
    db: AsyncSession = Depends(get_db)
):
    return await MovieController.get_movies(db, status, genre, page, limit)

@router.get("/{id}", response_model=MovieResponse)
async def get_movie_detail(id: int, db: AsyncSession = Depends(get_db)):
    return await MovieController.get_movie_by_id(db, id)


# --- ADMIN ENDPOINTS ---

@router.get("/sync/", dependencies=[Depends(verify_admin)])
async def sync_movie_data(title: str = Query(..., description="Tên phim cần lấy thông tin")):
    tmdb_id = await MovieSyncService.search_tmdb_movie(title)
    if not tmdb_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy phim trên TMDB.")
    
    details = await MovieSyncService.get_tmdb_details(tmdb_id)
    if not details:
        raise HTTPException(status_code=404, detail="Không lấy được chi tiết phim.")
        
    result = {
        "title": details.get("title", ""),
        "description": details.get("overview", ""),
        "duration": details.get("runtime", 0),
        "genre": ", ".join([g["name"] for g in details.get("genres", [])]),
        "poster_url": f"https://image.tmdb.org/t/p/w500{details.get('poster_path', '')}" if details.get("poster_path") else "",
        "backdrop_url": f"https://image.tmdb.org/t/p/w1280{details.get('backdrop_path', '')}" if details.get("backdrop_path") else "",
        "director": "",
        "imdb_rating": 0.0,
        "language": details.get("original_language", "vi").upper(),
        "release_date": details.get("release_date", ""),
    }
    
    # Get director
    credits = details.get("credits", {}).get("crew", [])
    for crew in credits:
        if crew.get("job") == "Director":
            result["director"] = crew.get("name", "")
            break
            
    # Get OMDB info if imdb_id exists
    imdb_id = details.get("imdb_id")
    if imdb_id:
        omdb_data = await MovieSyncService.get_omdb_rating(imdb_id)
        if omdb_data and omdb_data.get("imdb_rating"):
            result["imdb_rating"] = omdb_data["imdb_rating"]
            
    return result

@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_admin)])
async def create_movie(movie_data: MovieCreate, db: AsyncSession = Depends(get_db)):
    return await MovieController.create_movie(db, movie_data)

@router.put("/{id}", response_model=MovieResponse, dependencies=[Depends(verify_admin)])
async def update_movie(id: int, movie_data: MovieCreate, db: AsyncSession = Depends(get_db)):
    return await MovieController.update_movie(db, id, movie_data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_admin)])
async def delete_movie(id: int, db: AsyncSession = Depends(get_db)):
    return await MovieController.delete_movie(db, id)