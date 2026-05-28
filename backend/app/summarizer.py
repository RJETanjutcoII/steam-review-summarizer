# app/summarizer.py
# Orchestrator: ties together analysis (ML) and generation (LLM) pipelines.

from concurrent.futures import ThreadPoolExecutor

from .analysis import extract_sentences, cluster_sentences, extract_cluster_topic
from .generator import generate_summary


def _generate_for_cluster(args):
    cluster_sents, keywords, polarity = args
    return generate_summary(cluster_sents, keywords, polarity)


def summarize_reviews_aggregate(pos_reviews: list, neg_reviews: list) -> dict:
    """
    Hybrid summarization pipeline:
    1. Extract and filter opinion sentences from reviews
    2. Cluster sentences by semantic similarity (sentence embeddings)
    3. Identify each cluster's topic via TF-IDF
    4. Generate a clean summary sentence per cluster via LLM (in parallel)
    """
    result = {
        "praised": [],
        "criticized": [],
    }

    pos_sentences = extract_sentences(pos_reviews)
    neg_sentences = extract_sentences(neg_reviews)

    print(f"Extracted {len(pos_sentences)} positive, {len(neg_sentences)} negative sentences")

    if len(pos_sentences) >= 4:
        n_pos = max(5, min(8, len(pos_sentences) // 20))
        pos_clusters = cluster_sentences(pos_sentences, n_pos)
        max_points = 3 if len(pos_sentences) < 30 else (5 if len(pos_sentences) >= 60 else 4)

        tasks = [
            (sents, extract_cluster_topic(sents, pos_clusters), "positive")
            for sents, _ in pos_clusters
        ]

        with ThreadPoolExecutor() as executor:
            summaries = list(executor.map(_generate_for_cluster, tasks))

        seen = set()
        for summary in summaries:
            if len(result["praised"]) >= max_points:
                break
            if summary and summary not in seen:
                seen.add(summary)
                result["praised"].append(summary)

    if len(neg_sentences) >= 4:
        n_neg = max(3, min(8, len(neg_sentences) // 10))
        neg_clusters = cluster_sentences(neg_sentences, n_neg)
        max_points = 3 if len(neg_sentences) < 20 else (5 if len(neg_sentences) >= 40 else 4)

        tasks = [
            (sents, extract_cluster_topic(sents, neg_clusters), "negative")
            for sents, _ in neg_clusters
        ]

        with ThreadPoolExecutor() as executor:
            summaries = list(executor.map(_generate_for_cluster, tasks))

        seen = set()
        for summary in summaries:
            if len(result["criticized"]) >= max_points:
                break
            if summary and summary not in seen:
                seen.add(summary)
                result["criticized"].append(summary)

    if not result["praised"]:
        result["praised"] = ["No consistent praise found."]
    if not result["criticized"]:
        result["criticized"] = ["No major criticisms."]

    return result
