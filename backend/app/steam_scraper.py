# steam_scraper.py
# Handles all communication with the Steam API.

import requests

SEARCH_URL = "https://steamcommunity.com/actions/SearchApps/"


def search_games(query: str) -> list:
    """
    Search Steam for games matching a query string.
    Returns a list of { appid, name } objects for the autocomplete dropdown.

    This calls the same endpoint Steam's own search bar uses —
    it's fast and returns up to ~20 results.
    """
    query = query.strip()
    if not query:
        return []

    url = SEARCH_URL + requests.utils.quote(query)

    try:
        resp = requests.get(url, timeout=5)
        results = resp.json()
    except Exception:
        return []

    # Return only the fields the frontend needs (appid + name)
    return [{"appid": r["appid"], "name": r["name"]} for r in results]


def get_reviews_by_id(app_id: str, target_per_side: int = 75):
    """
    Fetch positive and negative reviews independently for a Steam app ID.
    Fetches each side separately so skewed games (e.g. 95% positive) still
    get enough negative reviews for meaningful criticism bullets.

    Returns: (pos_reviews, neg_reviews, game_name)
    """
    game_name = _get_game_name(app_id)
    pos_reviews = _fetch_reviews(app_id, "positive", target_per_side)
    neg_reviews = _fetch_reviews(app_id, "negative", target_per_side)
    return pos_reviews, neg_reviews, game_name


def _fetch_reviews(app_id: str, review_type: str, target: int) -> list:
    base_url = f"https://store.steampowered.com/appreviews/{app_id}"
    reviews = []
    cursor = "*"

    while len(reviews) < target:
        params = {
            "json": 1,
            "num_per_page": 100,
            "filter": "recent",
            "language": "english",
            "review_type": review_type,
            "cursor": cursor,
        }
        try:
            resp = requests.get(base_url, params=params, timeout=10)
            if resp.status_code != 200:
                break
            data = resp.json()
            page = data.get("reviews", [])
            if not page:
                break
            reviews.extend(r["review"] for r in page if len(r["review"].split()) >= 15)
            cursor = data.get("cursor", "")
            if not cursor or len(page) < 100:
                break
        except Exception:
            break

    return reviews[:target]


def _get_game_name(app_id: str) -> str:
    """
    Look up a game's name from its app ID using Steam's store API.
    Falls back to "Unknown Game" if the API fails.
    """
    try:
        resp = requests.get(
            f"https://store.steampowered.com/api/appdetails?appids={app_id}",
            timeout=5,
        )
        data = resp.json()
        return data[str(app_id)]["data"]["name"]
    except Exception:
        return "Unknown Game"
