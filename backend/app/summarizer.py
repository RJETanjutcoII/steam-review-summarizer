# app/summarizer.py
# Orchestrator: ties together analysis (ML) and generation (LLM) pipelines.

from .analysis import extract_sentences, cluster_sentences, extract_cluster_topic
from .generator import generate_summary


def summarize_reviews_aggregate(pos_reviews: list, neg_reviews: list) -> dict:
    """
    Hybrid summarization pipeline:
    1. Extract and filter opinion sentences from reviews
    2. Cluster sentences by semantic similarity (sentence embeddings)
    3. Identify each cluster's topic via TF-IDF
    4. Generate a clean summary sentence per cluster via LLM
    """
    result = {
        "praised": [],
        "criticized": [],
    }

    pos_sentences = extract_sentences(pos_reviews)
    neg_sentences = extract_sentences(neg_reviews)

    print(f"Extracted {len(pos_sentences)} positive, {len(neg_sentences)} negative sentences")

    # Cluster and summarize positive themes
    if len(pos_sentences) >= 4:
        # More sentences = more clusters to discover more topics
        n_pos = max(5, min(8, len(pos_sentences) // 20))
        pos_clusters = cluster_sentences(pos_sentences, n_pos)

        # Aim for 3-5 points based on sentence volume
        max_points = 3 if len(pos_sentences) < 30 else (5 if len(pos_sentences) >= 60 else 4)

        seen = set()
        # Try more clusters than max_points, since some may get filtered
        # out for being too vague. We stop once we have enough good ones.
        for cluster_sents, size in pos_clusters:
            if len(result["praised"]) >= max_points:
                break
            keywords = extract_cluster_topic(cluster_sents, pos_clusters)
            summary = generate_summary(cluster_sents, keywords, "positive")
            if summary and summary not in seen:
                seen.add(summary)
                result["praised"].append(summary)

    # Cluster and summarize negative themes
    if len(neg_sentences) >= 4:
        n_neg = max(3, min(8, len(neg_sentences) // 10))
        neg_clusters = cluster_sentences(neg_sentences, n_neg)

        max_points = 3 if len(neg_sentences) < 20 else (5 if len(neg_sentences) >= 40 else 4)

        seen = set()
        for cluster_sents, size in neg_clusters:
            if len(result["criticized"]) >= max_points:
                break
            keywords = extract_cluster_topic(cluster_sents, neg_clusters)
            summary = generate_summary(cluster_sents, keywords, "negative")
            if summary and summary not in seen:
                seen.add(summary)
                result["criticized"].append(summary)

    # Fallbacks
    if not result["praised"]:
        result["praised"] = ["No consistent praise found."]
    if not result["criticized"]:
        result["criticized"] = ["No major criticisms."]

    return result
