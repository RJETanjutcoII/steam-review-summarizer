# app/summarizer.py
from typing import List
from transformers import pipeline

# Load once at import time so we don't reload per request
# You can swap the model later for something smaller/faster.
_SUMMARIZER = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    tokenizer="facebook/bart-large-cnn",
    device_map="auto",       # uses GPU if available, CPU if not
)


def build_corpus(reviews: List[str], max_chars: int = 4000) -> str:
    """
    Join multiple reviews into a single text block, truncated to max_chars
    so we don't blow up the model context.
    """
    if not reviews:
        return ""

    joined = " ".join(reviews)
    if len(joined) > max_chars:
        joined = joined[:max_chars]

    return joined


def summarize_reviews(
    reviews: List[str],
    max_length: int = 150,
    min_length: int = 50,
) -> str:
    """
    Summarize a list of review texts into a single short summary.
    """
    corpus = build_corpus(reviews)
    if not corpus.strip():
        return "No reviews available to summarize."

    result = _SUMMARIZER(
        corpus,
        max_length=max_length,
        min_length=min_length,
        do_sample=False,      # deterministic output
    )

    # HF pipelines return a list of dicts like [{"summary_text": "..."}]
    return result[0]["summary_text"]
