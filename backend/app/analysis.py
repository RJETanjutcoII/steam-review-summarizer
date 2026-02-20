# app/analysis.py
# Preprocessing, sentence embeddings, clustering, and TF-IDF topic extraction.

from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from better_profanity import profanity
import numpy as np
import re

# Initialize profanity filter
profanity.load_censor_words()

# Lazy-load embedding model on first request (not at startup)
# so the server can bind its port immediately on Render.
_embedder = None

def _get_embedder():
    global _embedder
    if _embedder is None:
        print("Loading sentence transformer model...")
        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded!")
    return _embedder

# Extra stop words too generic for game review topic labels
_STOP_WORDS = [
    "game", "games", "play", "played", "playing", "player", "players",
    "really", "just", "like", "much", "even", "also", "still", "one",
    "get", "got", "good", "bad", "make", "made", "thing", "things",
    "way", "lot", "time", "going", "want", "know", "think", "feel",
    "ever", "best", "would", "could", "great", "pretty", "well",
    "many", "don", "doesn", "didn", "isn", "wasn", "can", "actually",
    "new", "first", "back", "right", "years", "year", "say",
    "people", "every", "something", "sure", "little",
]


def _clean_text(text: str) -> str:
    """Basic cleanup: strip HTML/BBCode tags, collapse whitespace."""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\[/?[a-zA-Z]+[^\]]*\]', '', text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _is_english(text: str) -> bool:
    """Quick check if text is mostly English (ASCII letters)."""
    if not text:
        return False
    ascii_letters = sum(1 for c in text if c.isascii() and c.isalpha())
    total_letters = sum(1 for c in text if c.isalpha())
    if total_letters == 0:
        return False
    return (ascii_letters / total_letters) > 0.8


def _is_opinion_sentence(sent: str) -> bool:
    """Check if a sentence expresses an opinion about the game."""
    lower = sent.lower().strip()

    personal_starts = [
        "i remember", "i was", "i am", "i used to", "i played this when",
        "i first", "when i was", "back in", "my friend", "my dad",
        "my brother", "my sister", "my mom", "one time",
        "in a way", "i think i",
    ]
    for start in personal_starts:
        if lower.startswith(start):
            return False

    opinion_words = [
        "game", "gameplay", "graphics", "music", "soundtrack", "story",
        "combat", "controls", "fun", "boring", "great", "terrible",
        "best", "worst", "amazing", "awful", "good", "bad", "love",
        "hate", "recommend", "worth", "overrated", "underrated",
        "solid", "broken", "buggy", "polished", "masterpiece",
        "enjoyable", "frustrating", "addicting", "addictive",
        "beautiful", "ugly", "dated", "classic", "unique",
        "repetitive", "challenging", "easy", "difficult",
        "multiplayer", "singleplayer", "players", "community",
        "update", "abandoned", "developers", "valve",
        "bots", "cheaters", "hackers", "f2p", "free",
        "classes", "weapons", "maps", "content",
    ]

    return sum(1 for w in opinion_words if w in lower) >= 1


def extract_sentences(reviews: list) -> list:
    """Extract clean, English, opinion-based sentences from reviews."""
    sentences = []

    for review in reviews:
        if not review or not review.strip():
            continue

        text = _clean_text(review)

        if not _is_english(text):
            continue

        if profanity.contains_profanity(text):
            text = profanity.censor(text)
            text = re.sub(r'[♥*]+', '', text)
            text = re.sub(r'\s+', ' ', text).strip()

        raw_sentences = re.split(r'(?<=[.!?])\s+', text)

        for sent in raw_sentences:
            sent = sent.strip()

            if len(sent) < 20 or len(sent) > 150:
                continue
            if sent.count(' ') < 3:
                continue
            if re.search(r'https?://', sent):
                continue
            if not _is_english(sent):
                continue
            if not _is_opinion_sentence(sent):
                continue

            sentences.append(sent)

    return sentences


def cluster_sentences(sentences: list, n_clusters: int) -> list:
    """
    Cluster sentences by semantic similarity using sentence embeddings.
    Returns list of (cluster_sentences, cluster_size) sorted by size.
    """
    if len(sentences) < n_clusters:
        n_clusters = max(2, len(sentences) // 2)

    if len(sentences) < 2:
        return [(sentences, len(sentences))]

    embeddings = _get_embedder().encode(sentences, show_progress_bar=False)
    embeddings = np.array(embeddings)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_ids = kmeans.fit_predict(embeddings)

    clusters = []
    for cluster_id in range(n_clusters):
        cluster_indices = np.where(cluster_ids == cluster_id)[0]

        if len(cluster_indices) < 2:
            continue

        cluster_sents = [sentences[i] for i in cluster_indices]
        clusters.append((cluster_sents, len(cluster_indices)))

    clusters.sort(key=lambda x: x[1], reverse=True)
    return clusters


def extract_cluster_topic(cluster_sents: list, all_clusters: list) -> list:
    """
    Use TF-IDF to find the distinctive keywords for a cluster
    compared to other clusters.
    """
    documents = [" ".join(sents) for sents, _ in all_clusters]

    tfidf = TfidfVectorizer(
        max_features=200,
        stop_words=_STOP_WORDS + list(TfidfVectorizer(stop_words='english').get_stop_words()),
        ngram_range=(1, 2),
        min_df=1,
    )

    try:
        tfidf_matrix = tfidf.fit_transform(documents)
    except ValueError:
        return []

    feature_names = tfidf.get_feature_names_out()

    target_doc = " ".join(cluster_sents)
    target_idx = None
    for i, (sents, _) in enumerate(all_clusters):
        if " ".join(sents) == target_doc:
            target_idx = i
            break

    if target_idx is None:
        return []

    scores = tfidf_matrix[target_idx].toarray().flatten()
    top_indices = scores.argsort()[-5:][::-1]
    keywords = [feature_names[i] for i in top_indices if scores[i] > 0]

    return keywords
