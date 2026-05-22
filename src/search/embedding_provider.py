import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingProvider:
    """
    Local open-source embeddings using SentenceTransformers.
    Model: sentence-transformers/all-MiniLM-L6-v2 (384 dims)
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        vectors = self.model.encode(texts, show_progress_bar=False)
        return np.asarray(vectors, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        vec = self.model.encode([query], show_progress_bar=False)
        return np.asarray(vec, dtype=np.float32)