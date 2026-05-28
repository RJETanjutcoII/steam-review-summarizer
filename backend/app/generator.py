# app/generator.py
# OpenRouter LLM integration for summary generation.

from dotenv import load_dotenv
import requests
import os
import re

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "deepseek/deepseek-v4-flash"


def generate_summary(cluster_sents: list, keywords: list, polarity: str) -> str:
    """
    Use OpenRouter LLM to generate a clean summary sentence
    from a cluster's representative sentences and TF-IDF keywords.
    """
    sample = cluster_sents[:8]
    sentiment = "positive" if polarity == "positive" else "negative"

    filtered_keywords = [k for k in keywords if _is_game_related(k)]
    keyword_str = ", ".join(filtered_keywords[:3]) if filtered_keywords else "general"
    action = "love about" if sentiment == "positive" else "hate about"
    prompt = (
        f"Reviews: {' | '.join(sample)}\n"
        f"Focus topic: {keyword_str}\n\n"
        f"Based only on the reviews above, write a short phrase (under 8 words) describing what players {action} about this game. "
        f"Rules: ONE phrase only. Describe a specific game feature visible in the reviews (e.g. story, writing, art style, music, mechanics, controls, difficulty, characters, performance). "
        f"Do NOT copy words or phrases verbatim from the reviews. Do NOT describe aspects not mentioned in the reviews. "
        f"Bad: 'Said giant laggy radius', 'Reputation praised', 'Expansive masterpiece story', 'Players enjoy gameplay'. "
        f"Good: 'Addictive class-based combat', 'Rampant bot infestation ruins matches', 'Satisfying weapon variety'. "
        f"No dashes, bullets, quotes, or period at the end."
    )

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 50,
            "temperature": 0.3,
        },
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()
    if "choices" not in data or not data["choices"][0]["message"]["content"]:
        return None
    summary = data["choices"][0]["message"]["content"].strip()

    # Clean up: take only the first line, strip markers/quotes/punctuation
    summary = summary.split('\n')[0].strip()
    summary = re.sub(r'^[-•*]+\s*', '', summary)  # strip leading bullet markers
    summary = summary.strip('"\'')
    summary = re.sub(r'\s+', ' ', summary).strip()
    summary = summary.rstrip('.')
    if summary:
        summary = summary[0].upper() + summary[1:]

    # If the model still crammed multiple items with dashes/separators, take the first
    if ' - ' in summary:
        summary = summary.split(' - ')[0].strip()

    if _is_artifact(summary):
        return None

    if _is_vague(summary):
        return None

    if _wrong_sentiment(summary, polarity):
        return None

    return summary


_GAME_VOCAB = {
    "gameplay", "graphics", "music", "soundtrack", "story", "narrative", "plot",
    "combat", "controls", "mechanics", "mechanic", "difficulty", "performance",
    "characters", "character", "dialogue", "writing", "art", "animation",
    "multiplayer", "singleplayer", "community", "content", "levels", "maps",
    "weapons", "classes", "abilities", "skills", "progression", "leveling",
    "bugs", "crashes", "optimization", "fps", "lag", "loading",
    "price", "dlc", "microtransactions", "replayability", "pacing", "atmosphere",
    "voice", "puzzle", "puzzles", "platforming", "movement", "exploration",
    "lore", "world", "ending", "choices", "soundtrack", "boss", "bosses",
    "cheaters", "bots", "servers", "matchmaking", "updates", "developers",
}


def _is_game_related(keyword: str) -> bool:
    lower = keyword.lower()
    return any(vocab_word in lower for vocab_word in _GAME_VOCAB)


def _is_artifact(summary: str) -> bool:
    lower = summary.lower()
    artifact_starts = ["said ", "says ", "very ", "so ", "i ", "you ", "we ", "they "]
    return any(lower.startswith(s) for s in artifact_starts)


def _is_vague(summary: str) -> bool:
    """
    Check if a summary is too vague to be useful.
    A good summary names a specific aspect: "Frustrating combat mechanics"
    A bad summary is just generic sentiment: "Can't recommend or enjoy the game"
    """
    lower = summary.lower()

    # Generic phrases that say nothing about WHAT is good/bad
    vague_phrases = [
        "enjoy the game", "would recommend", "don't recommend", "not recommended", "not worth", "waste of time",
        "waste of money", "don't buy", "must buy", "must play",
        "great game", "bad game", "good game", "terrible game",
        "love this game", "hate this game", "best game", "worst game",
        "not fun", "very fun", "so fun", "no fun",
        "overall experience", "mixed feelings",
    ]
    return any(phrase in lower for phrase in vague_phrases)


def _wrong_sentiment(summary: str, polarity: str) -> bool:
    """
    Check if a summary's sentiment contradicts its intended polarity.
    Catches cases like "Alt-tabbing causes crashes" appearing as praise,
    or "Beautiful open world" appearing as criticism.
    """
    lower = summary.lower()

    # Words/phrases that signal negative sentiment
    negative_signals = [
        "crash", "bug", "broken", "frustrat", "boring", "tedious",
        "annoying", "terrible", "awful", "horrible", "worst",
        "lack", "missing", "empty", "dead", "unbalanced",
        "repetitive", "grindy", "clunky", "outdated", "dated",
        "overpriced", "abandoned", "toxic", "unfair", "poor",
        "fails", "failure", "disappointing", "uninspired",
        "lag", "laggy", "stutter", "fps", "slow", "freeze",
    ]

    # Words/phrases that signal positive sentiment
    positive_signals = [
        "beautiful", "stunning", "amazing", "excellent", "fantastic",
        "satisfying", "rewarding", "immersive", "engaging", "polished",
        "innovative", "unique", "rich", "deep", "solid", "smooth",
        "masterpiece", "brilliant", "charming", "beloved", "peak",
        "addictive", "compelling", "enjoyable", "impressive",
    ]

    if polarity == "positive":
        neg_hits = sum(1 for w in negative_signals if w in lower)
        pos_hits = sum(1 for w in positive_signals if w in lower)
        return neg_hits >= 2 and pos_hits == 0

    else:
        pos_hits = sum(1 for w in positive_signals if w in lower)
        neg_hits = sum(1 for w in negative_signals if w in lower)
        return pos_hits >= 2 and neg_hits == 0
