from pathlib import Path
import os
import secrets
import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader

load_dotenv(Path(__file__).with_name(".env"))
TMDB_KEY = os.environ.get("TMDB_API_KEY", "")
GAME_KEY = os.environ.get("GAME_API_KEY", "")
MOVIE_ID = int(os.environ.get("MOVIE_ID", "603"))
if not TMDB_KEY or len(GAME_KEY) < 32 or MOVIE_ID <= 0:
    raise RuntimeError("Configure TMDB_API_KEY, a random GAME_API_KEY and a positive MOVIE_ID")

app = FastAPI(title="Movie guessing game")
key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_game_key(value: str | None = Depends(key_header)):
    if value is None or not secrets.compare_digest(value.encode(), GAME_KEY.encode()):
        raise HTTPException(401, "Invalid or missing game key", headers={"WWW-Authenticate": "APIKey"})

def get_movie():
    try:
        response = httpx.get(
            f"https://api.themoviedb.org/3/movie/{MOVIE_ID}",
            params={"api_key": TMDB_KEY, "language": "en-GB"}, timeout=5.0,
        )
        response.raise_for_status()
        data = response.json()
        # Validate only the small subset used by this lesson.
        title = data["title"]
        date = data["release_date"]
        genres = [g["name"] for g in data["genres"]]
        runtime = data["runtime"]
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Missing title")
        if not isinstance(date, str) or len(date) < 4 or not date[:4].isdigit():
            raise ValueError("Missing release year")
        if not all(isinstance(g, str) for g in genres):
            raise ValueError("Invalid genres")
        if runtime is not None and (type(runtime) is not int or runtime < 0):
            raise ValueError("Invalid runtime")
        return {"title": title, "year": int(date[:4]), "genres": genres, "runtime": runtime}
    except httpx.TimeoutException:
        raise HTTPException(504, "Movie service timed out") from None
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 429:
            raise HTTPException(503, "Movie service temporarily unavailable") from None
        raise HTTPException(502, "Movie service request failed") from None
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        raise HTTPException(502, "Movie service unavailable or invalid response") from None

@app.get("/movie/clue")
def clue():
    movie = get_movie()
    return {"year": movie["year"], "genres": movie["genres"], "runtime": movie["runtime"]}

@app.get("/movie/answer", dependencies=[Depends(require_game_key)])
def answer():
    return {"title": get_movie()["title"]}
