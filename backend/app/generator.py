# app/generator.py
# OpenRouter LLM integration for summary generation.

from dotenv import load_dotenv
import requests
import os
import re

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "arcee-ai/trinity-large-preview:free"


def generate_summary(cluster_sents: list, keywords: list, polarity: str) -> str:
    """
    Use OpenRouter LLM to generate a clean summary sentence
    from a cluster's representative sentences and TF-IDF keywords.
    """
    sample = cluster_sents[:8]
    keyword_str = ", ".join(keywords[:3]) if keywords else "general"

    sentiment = "positive" if polarity == "positive" else "negative"

    prompt = (
        f"These {sentiment} game reviews mention: {keyword_str}\n"
        f"Reviews: {' | '.join(sample)}\n\n"
        f"Respond with ONLY a single short phrase (under 8 words) summarizing the {sentiment} sentiment about {keyword_str}. "
        f"Rules: ONE phrase only. No dashes, no bullet points, no lists, no quotes, no explanation. "
        f"Must name a specific game aspect (e.g. combat, story, graphics, music, maps, UI, performance). "
        f"NEVER use vague phrases like 'enjoy the game', 'recommend', 'not worth it', or 'waste of time'. "
        f"Do NOT start with 'The game' or 'Players'. No period at the end."
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
    summary = data["choices"][0]["message"]["content"].strip()

    # Clean up: take only the first line, strip markers/quotes/punctuation
    summary = summary.split('\n')[0].strip()
    summary = re.sub(r'^[-•*]+\s*', '', summary)  # strip leading bullet markers
    summary = summary.strip('"\'')
    summary = re.sub(r'\s+', ' ', summary).strip()
    summary = summary.rstrip('.')

    # If the model still crammed multiple items with dashes/separators, take the first
    if ' - ' in summary:
        summary = summary.split(' - ')[0].strip()

    # Reject vague summaries that don't mention a specific game aspect.
    if _is_vague(summary):
        return None

    # Reject summaries whose sentiment contradicts the polarity.
    # e.g. "Alt-tabbing causes crashes" should NOT appear as praise.
    if _wrong_sentiment(summary, polarity):
        return None

    return summary


def _is_vague(summary: str) -> bool:
    """
    Check if a summary is too vague to be useful.
    A good summary names a specific aspect: "Frustrating combat mechanics"
    A bad summary is just generic sentiment: "Can't recommend or enjoy the game"
    """
    lower = summary.lower()

    # Generic phrases that say nothing about WHAT is good/bad
    vague_phrases = [
        "enjoy the game", "recommend", "not worth", "waste of time",
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
        # If it's supposed to be praise but sounds negative, reject it
        neg_hits = sum(1 for w in negative_signals if w in lower)
        pos_hits = sum(1 for w in positive_signals if w in lower)
        return neg_hits > 0 and pos_hits == 0

    else:
        # If it's supposed to be criticism but sounds positive, reject it
        pos_hits = sum(1 for w in positive_signals if w in lower)
        neg_hits = sum(1 for w in negative_signals if w in lower)
        return pos_hits > 0 and neg_hits == 0
