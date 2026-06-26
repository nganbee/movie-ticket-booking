import httpx
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY") or os.getenv("THEMOIVE_API_KEY")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

def get_tmdb_headers():
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_KEY}"
    }

class MovieSyncService:
    @staticmethod
    async def search_tmdb_movie(title: str):
        if not TMDB_API_KEY:
            raise ValueError("Thiếu cấu hình TMDB_API_KEY hoặc THEMOIVE_API_KEY trong .env")
            
        url = f"https://api.themoviedb.org/3/search/movie?query={urllib.parse.quote(title)}&language=vi-VN"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=get_tmdb_headers())
            if res.status_code == 200:
                data = res.json()
                if data.get("results"):
                    return data["results"][0]["id"]
        return None

    @staticmethod
    async def get_tmdb_details(tmdb_id: int):
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=vi-VN&append_to_response=credits,videos"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=get_tmdb_headers())
            if res.status_code == 200:
                return res.json()
        return None

    @staticmethod
    async def get_omdb_rating(imdb_id: str):
        if not OMDB_API_KEY:
            raise ValueError("Thiếu cấu hình OMDB_API_KEY trong .env")
            
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            if res.status_code == 200:
                data = res.json()
                if data.get("Response") == "True":
                    rating_str = data.get("imdbRating", "0")
                    votes_str = data.get("imdbVotes", "0").replace(",", "")
                    try:
                        return {
                            "imdb_rating": float(rating_str) if rating_str != "N/A" else None,
                            "imdb_votes": int(votes_str) if votes_str != "N/A" else None
                        }
                    except ValueError:
                        return None
        return None
