import requests

def get_app_id(game_name):
    """Get Steam App ID from search."""
    url = "https://steamcommunity.com/actions/SearchApps/" + game_name
    response = requests.get(url)
    results = response.json()
    if not results:
        return None
    return results[0]['appid']


def get_reviews(game_name, num_reviews=100):
    """Get positive and negative reviews from Steam."""
    app_id = get_app_id(game_name)
    if not app_id:
        return [], []

    base_url = f"https://store.steampowered.com/appreviews/{app_id}"
    params = {
        "json": 1,
        "num_per_page": 100,
        "filter": "recent",
        "language": "english"
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return [], []

    all_reviews = response.json().get("reviews", [])

    pos_reviews = [r["review"] for r in all_reviews if r["voted_up"]]
    neg_reviews = [r["review"] for r in all_reviews if not r["voted_up"]]

    return pos_reviews[:num_reviews], neg_reviews[:num_reviews]
