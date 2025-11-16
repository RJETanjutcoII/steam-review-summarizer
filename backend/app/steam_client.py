# app/steam_client.py
import requests
from typing import List

STEAM_REVIEWS_URL = "https://store.steampowered.com/appreviews/{appid}"


def fetch_reviews(appid: int, max_reviews: int = 40, timeout: int = 10) -> List[str]:
    """
    Fetch recent reviews for a game from Steam's public reviews endpoint.

    Note: This is a simple first version – it grabs up to `max_reviews`
    from the 'recent' filter in a single call.
    """
    params = {
        "json": 1,
        "filter": "recent",       # recent or all
        "language": "english",    # you can change this later
        "num_per_page": max_reviews,
        "purchase_type": "all",
    }

    resp = requests.get(
        STEAM_REVIEWS_URL.format(appid=appid),
        params=params,
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()

    reviews = data.get("reviews", [])
    texts: List[str] = []

    for r in reviews:
        text = r.get("review", "")
        if text:
            texts.append(text.strip())

    return texts
