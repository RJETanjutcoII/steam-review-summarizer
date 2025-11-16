from fastapi import FastAPI, Query
from steam_scraper import get_reviews
from summarizer import summarize_reviews

app = FastAPI()

@app.get("/summarize")
async def summarize(game_name: str = Query(..., description="Name of the game to analyze")):
    pos_reviews, neg_reviews = get_reviews(game_name)

    pos_summary = summarize_reviews(pos_reviews)
    neg_summary = summarize_reviews(neg_reviews)

    return {
        "game": game_name,
        "positive_summary": pos_summary,
        "negative_summary": neg_summary
    }
