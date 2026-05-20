# src/routes/movies.py
from fastapi import APIRouter, Query, Depends, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.movie import MovieResponse, MovieCreate
from src.controllers.movie_controller import MovieController
from src.config.db import get_db
from src.middlewares.auth import verify_admin

router = APIRouter()

# --- PUBLIC ENDPOINTS ---

@router.get("/", response_model=List[MovieResponse])
async def get_movies(
    status: Optional[str] = Query(None, description="now_showing hoặc coming_soon"),
    genre: Optional[str] = Query(None, description="Thể loại phim"),
    db: AsyncSession = Depends(get_db)
):
    return await MovieController.get_movies(db, status, genre)

@router.get("/{id}", response_model=MovieResponse)
async def get_movie_detail(id: int, db: AsyncSession = Depends(get_db)):
    return await MovieController.get_movie_by_id(db, id)


# --- ADMIN ENDPOINTS ---

@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_admin)])
async def create_movie(movie_data: MovieCreate, db: AsyncSession = Depends(get_db)):
    return await MovieController.create_movie(db, movie_data)

@router.put("/{id}", response_model=MovieResponse, dependencies=[Depends(verify_admin)])
async def update_movie(id: int, movie_data: MovieCreate, db: AsyncSession = Depends(get_db)):
    return await MovieController.update_movie(db, id, movie_data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_admin)])
async def delete_movie(id: int, db: AsyncSession = Depends(get_db)):
    return await MovieController.delete_movie(db, id)