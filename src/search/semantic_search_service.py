import json
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import faiss
import re

from src.config import (
    EMBEDDING_MODEL_NAME,
    SEMANTIC_INDEX_ROOT,
    SEMANTIC_ACTIVE_INDEX_FILE,
)
from src.search.embedding_provider import EmbeddingProvider


DEFAULT_TOP_K = 5
MAX_TOP_K = 20


class SemanticIndexStore:
    """
    In-memory semantic index holder with:
     FAISS semantic search
     Keyword search (customer_id, order_id)
     Bucket filtering (amount + recency)
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._embedder = EmbeddingProvider(EMBEDDING_MODEL_NAME)

        self._index: Optional[faiss.Index] = None
        self._metadata: Optional[List[Dict[str, Any]]] = None
        self._manifest: Optional[Dict[str, Any]] = None

        self._active_slot: Optional[str] = None
        self._active_index_dir: Optional[str] = None
        self._index_version: Optional[str] = None

    # ----------------------------
    # LOAD INDEX
    # ----------------------------
    def _read_active_pointer(self) -> Dict[str, Any]:
        pointer_path = Path(SEMANTIC_ACTIVE_INDEX_FILE)
        if not pointer_path.exists():
            raise FileNotFoundError("Active index pointer not found")
        with pointer_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def load_active_from_disk(self) -> Dict[str, Any]:
        pointer = self._read_active_pointer()

        active_index_dir = pointer.get("active_index_dir")
        if not active_index_dir:
            active_index_dir = str(Path(SEMANTIC_INDEX_ROOT) / pointer["active_slot"])

        idx_dir = Path(active_index_dir)

        index = faiss.read_index(str(idx_dir / "orders.faiss"))

        with (idx_dir / "metadata.json").open("r", encoding="utf-8") as f:
            metadata = json.load(f)

        with (idx_dir / "manifest.json").open("r", encoding="utf-8") as f:
            manifest = json.load(f)

        with self._lock:
            self._index = index
            self._metadata = metadata
            self._manifest = manifest
            self._active_index_dir = active_index_dir

        return {
            "documents_indexed": len(metadata),
        }

    def reload_active(self):
        return self.load_active_from_disk()

    def status(self):
        return {"loaded": self._index is not None}

    # ----------------------------
    # UTILS
    # ----------------------------
    @staticmethod
    def _normalize_query_vec(vec):
        vec = np.asarray(vec, dtype=np.float32)
        faiss.normalize_L2(vec)
        return vec

    # ----------------------------
    # FINAL SEARCH (HYBRID + FILTER)
    # ----------------------------
    def search(self, query: str, top_k: int = DEFAULT_TOP_K) -> List[Dict[str, Any]]:

        top_k = max(1, min(int(top_k), MAX_TOP_K))

        with self._lock:
            if self._index is None or self._metadata is None:
                raise FileNotFoundError("Index not loaded")
            index = self._index
            metadata = self._metadata

        # -----------------------------
        # 1. VECTOR SEARCH
        # -----------------------------
        qvec = self._embedder.embed_query(query).astype(np.float32)
        qvec = self._normalize_query_vec(qvec)

        fetch_k = min(max(top_k * 4, top_k), len(metadata))

        scores, ids = index.search(qvec, fetch_k)

        semantic_results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0:
                continue
            semantic_results.append({
                "idx": int(idx),
                "score": float(score),
                "row": metadata[idx]
            })

        # -----------------------------
        # 2. KEYWORD SEARCH
        # -----------------------------
        keyword_results = []

        customer_matches = re.findall(r'C\d+', query.upper())
        order_matches = re.findall(r'\d+', query)

        for i, row in enumerate(metadata):

            if customer_matches:
                if str(row.get("customer_id", "")).upper() in customer_matches:
                    keyword_results.append({
                        "idx": i,
                        "score": 1.0,
                        "row": row
                    })

            if order_matches:
                if str(row.get("order_id", "")) in order_matches:
                    keyword_results.append({
                        "idx": i,
                        "score": 1.0,
                        "row": row
                    })

        # -----------------------------
        # 3. MERGE RESULTS
        # -----------------------------
        combined = {}

        for r in semantic_results + keyword_results:
            idx = r["idx"]

            if idx not in combined:
                combined[idx] = r
            else:
                if r["score"] > combined[idx]["score"]:
                    combined[idx] = r

        # -----------------------------
        # 4. INTENT DETECTION (FILTER)
        # -----------------------------
        query_lower = query.lower()

        amount_filter = None
        date_filter = None

        # amount
        if any(w in query_lower for w in ["high", "expensive", "costly", "premium"]):
            amount_filter = {"high", "very high"}
        elif any(w in query_lower for w in ["low", "cheap", "budget"]):
            amount_filter = {"low", "very low"}
        elif "medium" in query_lower:
            amount_filter = {"medium"}

        # date
        if any(w in query_lower for w in ["recent", "latest", "new"]):
            date_filter = {"recent", "very recent"}
        elif "old" in query_lower:
            date_filter = {"old", "very old"}

        # -----------------------------
        # 5. APPLY FILTERS
        # -----------------------------
        filtered = []

        for r in combined.values():
            row = r["row"]

            if amount_filter:
                if row.get("amount_bucket") not in amount_filter:
                    continue

            if date_filter:
                if row.get("date_bucket") not in date_filter:
                    continue

            filtered.append(r)

        # -----------------------------
        # 6. SORT + FINAL OUTPUT
        # -----------------------------
        final_sorted = sorted(
            filtered,
            key=lambda x: x["score"],
            reverse=True
        )

        results = []
        for r in final_sorted:
            row = r["row"]

            results.append({
                "order_id": row.get("order_id"),
                "customer_id": row.get("customer_id"),
                "amount_usd": row.get("amount_usd"),
                "order_date": row.get("order_date"),
                "score": float(r["score"]),
            })

            if len(results) >= top_k:
                break

        return results


# ✅ Global instance
semantic_store = SemanticIndexStore()
