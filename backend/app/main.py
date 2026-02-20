import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .summarizer import summarize_reviews_aggregate
from .steam_scraper import search_games, get_reviews_by_id

app = FastAPI()

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search")
async def search(q: str = Query(..., min_length=1)):
    """Autocomplete endpoint — proxies Steam's search API."""
    return search_games(q)


@app.get("/summarize")
async def summarize(app_id: str = Query(..., min_length=1)):
    """Main summarization endpoint. Takes an app_id from the search dropdown."""
    pos_reviews, neg_reviews, game_name = get_reviews_by_id(app_id)
    summary = summarize_reviews_aggregate(pos_reviews, neg_reviews)

    return {
        "game": game_name,
        "app_id": app_id,
        "summary": summary,
    }


@app.get("/")
async def root():
    return {"status": "ok"}
