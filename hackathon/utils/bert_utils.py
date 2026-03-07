"""
BERT Utilities - Sentence embeddings and cosine similarity using sentence-transformers
Uses all-MiniLM-L6-v2 for fast, high-quality semantic similarity
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model once at module level (cached after first load)
_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print("[BERT] Loading sentence-transformers model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[BERT] Model loaded successfully.")
    return _model


def get_embedding(text: str) -> np.ndarray:
    """Encode a text string into a BERT embedding vector."""
    model = get_model()
    embedding = model.encode([text], convert_to_numpy=True)
    return embedding[0]


def compute_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
    """Compute cosine similarity between two embedding vectors. Returns 0.0-1.0."""
    e1 = emb1.reshape(1, -1)
    e2 = emb2.reshape(1, -1)
    score = cosine_similarity(e1, e2)[0][0]
    return float(max(0.0, min(1.0, score)))


def batch_embeddings(texts: list[str]) -> list[np.ndarray]:
    """Encode a list of texts into embeddings efficiently."""
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return list(embeddings)
