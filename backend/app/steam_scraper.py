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


def get_reviews_by_id(app_id: str, num_reviews: int = 100):
    """
    Fetch positive and negative reviews for a specific Steam app ID.
    Also fetches the game's name from the store API.

    Returns: (pos_reviews, neg_reviews, game_name)
    """
    # Get the game's name from Steam's store details API
    game_name = _get_game_name(app_id)

    base_url = f"https://store.steampowered.com/appreviews/{app_id}"
    params = {
        "json": 1,
        "num_per_page": 100,
        "filter": "recent",
        "language": "english",
    }

    try:
        resp = requests.get(base_url, params=params, timeout=10)
        if resp.status_code != 200:
            return [], [], game_name

        all_reviews = resp.json().get("reviews", [])
    except Exception:
        return [], [], game_name

    pos_reviews = [r["review"] for r in all_reviews if r.get("voted_up")]
    neg_reviews = [r["review"] for r in all_reviews if not r.get("voted_up")]

    return pos_reviews[:num_reviews], neg_reviews[:num_reviews], game_name


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
