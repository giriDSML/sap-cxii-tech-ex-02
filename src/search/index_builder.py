'''Recency_Value:
- latest 10 orders by order_date  -> recent
- oldest 10 orders by order_date  -> old
- others                          -> normal_recency

Monetary_Value:
- top 10 orders by amount_usd     -> expensive
- bottom 10 orders by amount_usd  -> cheap
- others                          -> medium_value

Recency_Monetary_Value:
- today based:
  - within last 30 days + amount >= 300 -> recent_expensive
  - within last 30 days + amount <= 50  -> recent_cheap
  - older than 1 year + amount >= 300   -> old_expensive
  - older than 1 year + amount <= 50    -> old_cheap
  - otherwise                           -> neutral_combo'''


import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import faiss

from src.config import (
    DB_PATH,
    SEMANTIC_INDEX_ROOT,
    SEMANTIC_ACTIVE_INDEX_FILE,
    EMBEDDING_MODEL_NAME,
)
from src.db_layer.sqlite_client import get_connection
from src.search.embedding_provider import EmbeddingProvider


BLUE_SLOT = "blue"
GREEN_SLOT = "green"


# -------------------------------------------------------
# Business rules
# -------------------------------------------------------
RANK_WINDOW_SIZE = 10

RECENT_DAYS = 30
OLD_DAYS = 365

EXPENSIVE_AMOUNT_THRESHOLD = 300.0
CHEAP_AMOUNT_THRESHOLD = 50.0


# -------------------------------------------------------
# Read orders from SQLite
# -------------------------------------------------------
def _read_orders_from_sqlite() -> list[dict]:
    conn = get_connection(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT
                order_id,
                customer_id,
                order_date,
                amount_usd,
                original_amount,
                original_currency
            FROM orders
            """
        ).fetchall()

        return [dict(r) for r in rows]

    finally:
        conn.close()


# -------------------------------------------------------
# Blue/green pointer management
# -------------------------------------------------------
def _read_active_pointer() -> dict | None:
    active_file = Path(SEMANTIC_ACTIVE_INDEX_FILE)

    if not active_file.exists():
        return None

    with active_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def _get_inactive_slot() -> str:
    pointer = _read_active_pointer()

    if not pointer:
        return BLUE_SLOT

    active_slot = pointer.get("active_slot")

    if active_slot == BLUE_SLOT:
        return GREEN_SLOT

    if active_slot == GREEN_SLOT:
        return BLUE_SLOT

    return BLUE_SLOT


def _slot_dir(slot: str) -> Path:
    return Path(SEMANTIC_INDEX_ROOT) / slot


# -------------------------------------------------------
# Safe conversion helpers
# -------------------------------------------------------
def _safe_float(x, default=0.0) -> float:
    try:
        if x is None or str(x).strip() == "":
            return default
        return float(x)
    except Exception:
        return default


def _parse_date(date_str: str) -> datetime | None:
    try:
        return datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
    except Exception:
        return None


def _format_date(date_str: str) -> tuple[str, str]:
    iso_date = (date_str or "").strip()

    if not iso_date:
        return "", ""

    dt = _parse_date(iso_date)

    if dt is None:
        return iso_date, iso_date

    return iso_date, dt.strftime("%B %d, %Y")


# -------------------------------------------------------
# Rank sets: latest 10, oldest 10, top 10 amount, bottom 10 amount
# -------------------------------------------------------
def _build_rank_sets(records: list[dict]) -> dict:
    """
    Builds rank-based groups.

    Recency:
      latest 10 records by order_date -> recent
      oldest 10 records by order_date -> old

    Monetary:
      top 10 records by amount_usd -> expensive
      bottom 10 records by amount_usd -> cheap
    """

    valid_dates: list[tuple[str, datetime]] = []
    valid_amounts: list[tuple[str, float]] = []

    for row in records:
        order_id = str(row.get("order_id", "")).strip()
        order_date = str(row.get("order_date", "")).strip()

        dt = _parse_date(order_date)
        amount = _safe_float(row.get("amount_usd"), 0.0)

        if order_id:
            if dt is not None:
                valid_dates.append((order_id, dt))

            valid_amounts.append((order_id, amount))

    latest_order_ids = {
        oid
        for oid, _ in sorted(
            valid_dates,
            key=lambda x: x[1],
            reverse=True,
        )[:RANK_WINDOW_SIZE]
    }

    oldest_order_ids = {
        oid
        for oid, _ in sorted(
            valid_dates,
            key=lambda x: x[1],
        )[:RANK_WINDOW_SIZE]
    }

    top_amount_order_ids = {
        oid
        for oid, _ in sorted(
            valid_amounts,
            key=lambda x: x[1],
            reverse=True,
        )[:RANK_WINDOW_SIZE]
    }

    bottom_amount_order_ids = {
        oid
        for oid, _ in sorted(
            valid_amounts,
            key=lambda x: x[1],
        )[:RANK_WINDOW_SIZE]
    }

    return {
        "latest_order_ids": latest_order_ids,
        "oldest_order_ids": oldest_order_ids,
        "top_amount_order_ids": top_amount_order_ids,
        "bottom_amount_order_ids": bottom_amount_order_ids,
    }


# -------------------------------------------------------
# Recency_Value
# -------------------------------------------------------
def _recency_value(order_id: str, rank_sets: dict) -> str:
    """
    Rank-based recency semantic label.
    """

    if order_id in rank_sets["latest_order_ids"]:
        return "recent"

    if order_id in rank_sets["oldest_order_ids"]:
        return "old"

    return "normal_recency"


def _date_bucket_from_recency_value(recency_value: str) -> str:
    """
    Keeps compatibility with semantic search service.
    """

    if recency_value == "recent":
        return "recent"

    if recency_value == "old":
        return "old"

    return "normal"


# -------------------------------------------------------
# Monetary_Value
# -------------------------------------------------------
def _monetary_value(order_id: str, rank_sets: dict) -> str:
    """
    Rank-based monetary semantic label.
    """

    if order_id in rank_sets["top_amount_order_ids"]:
        return "expensive"

    if order_id in rank_sets["bottom_amount_order_ids"]:
        return "cheap"

    return "medium_value"


def _amount_bucket_from_monetary_value(monetary_value: str) -> str:
    """
    Keeps compatibility with semantic search service.

    expensive -> very high
    cheap     -> very low
    medium    -> medium
    """

    if monetary_value == "expensive":
        return "very high"

    if monetary_value == "cheap":
        return "very low"

    return "medium"


# -------------------------------------------------------
# Today-based Recency_Monetary_Value
# -------------------------------------------------------
def _recency_monetary_value(
    amount: float,
    order_date: str,
    today: datetime,
    recent_days: int = RECENT_DAYS,
    old_days: int = OLD_DAYS,
    expensive_threshold: float = EXPENSIVE_AMOUNT_THRESHOLD,
    cheap_threshold: float = CHEAP_AMOUNT_THRESHOLD,
) -> str:
    """
    Business-rule based combined semantic label using TODAY as reference.

    Rules:
      recent = order_date within last 30 days from today
      old    = order_date older than 1 year from today

      expensive/high value = amount >= 300
      cheap/low value      = amount <= 50

    Labels:
      recent_expensive
      recent_cheap
      old_expensive
      old_cheap
      neutral_combo
    """

    dt = _parse_date(order_date)

    if dt is None:
        return "neutral_combo"

    recent_start_date = today - timedelta(days=recent_days)
    old_cutoff_date = today - timedelta(days=old_days)

    is_recent = recent_start_date <= dt <= today
    is_old = dt <= old_cutoff_date

    is_expensive = amount >= expensive_threshold
    is_cheap = amount <= cheap_threshold

    if is_recent and is_expensive:
        return "recent_expensive"

    if is_recent and is_cheap:
        return "recent_cheap"

    if is_old and is_expensive:
        return "old_expensive"

    if is_old and is_cheap:
        return "old_cheap"

    return "neutral_combo"


def _recency_monetary_phrases(recency_monetary_value: str) -> str:
    """
    Natural-language phrases added to embedded text.
    These improve semantic matching for combined queries.
    """

    if recency_monetary_value == "recent_expensive":
        return (
            "This is a recent expensive order. "
            "This is a recent high value order. "
            "This is a latest costly transaction. "
            "This order is both recent and expensive."
        )

    if recency_monetary_value == "recent_cheap":
        return (
            "This is a recent cheap order. "
            "This is a recent low value order. "
            "This is a latest budget transaction. "
            "This order is both recent and cheap."
        )

    if recency_monetary_value == "old_expensive":
        return (
            "This is an old expensive order. "
            "This is a historical high value order. "
            "This is an old costly transaction. "
            "This order is both old and expensive."
        )

    if recency_monetary_value == "old_cheap":
        return (
            "This is an old cheap order. "
            "This is a historical low value order. "
            "This is an old budget transaction. "
            "This order is both old and cheap."
        )

    return "This order has a neutral recency and monetary profile."


# -------------------------------------------------------
# Semantic text builder
# -------------------------------------------------------
def build_order_text(
    row: dict,
    rank_sets: dict,
    today: datetime,
) -> tuple[str, str, str, str, str, str]:
    """
    Returns:
      text,
      recency_value,
      monetary_value,
      recency_monetary_value,
      amount_bucket,
      date_bucket
    """

    order_id = str(row.get("order_id", "")).strip()
    customer_id = str(row.get("customer_id", "")).strip()

    amount = _safe_float(row.get("amount_usd"), 0.0)
    currency = str(row.get("original_currency") or "USD").strip().upper()

    date_str = str(row.get("order_date", "")).strip()
    iso_date, human_date = _format_date(date_str)

    recency_value = _recency_value(order_id, rank_sets)
    monetary_value = _monetary_value(order_id, rank_sets)

    amount_bucket = _amount_bucket_from_monetary_value(monetary_value)
    date_bucket = _date_bucket_from_recency_value(recency_value)

    recency_monetary_value = _recency_monetary_value(
        amount=amount,
        order_date=date_str,
        today=today,
    )

    recency_monetary_text = _recency_monetary_phrases(
        recency_monetary_value
    )

    text = (
        f"Order {order_id} belongs to customer {customer_id}. "
        f"The customer ID is {customer_id}. "

        f"The order amount is {amount} {currency}. "
        f"The monetary value is {monetary_value}. "
        f"This order can be described as {monetary_value}. "
        f"The amount bucket is {amount_bucket}. "

        f"The order date is {iso_date} ({human_date}). "
        f"The recency value is {recency_value}. "
        f"This order can be described as {recency_value}. "
        f"The date bucket is {date_bucket}. "

        f"The recency monetary value is {recency_monetary_value}. "
        f"{recency_monetary_text} "

        f"This purchase or transaction was made by customer {customer_id}. "

        f"Summary: "
        f"order_id={order_id}, "
        f"customer_id={customer_id}, "
        f"amount_usd={amount}, "
        f"order_date={iso_date}, "
        f"recency_value={recency_value}, "
        f"monetary_value={monetary_value}, "
        f"recency_monetary_value={recency_monetary_value}, "
        f"amount_bucket={amount_bucket}, "
        f"date_bucket={date_bucket}."
    )

    return (
        text,
        recency_value,
        monetary_value,
        recency_monetary_value,
        amount_bucket,
        date_bucket,
    )


# -------------------------------------------------------
# Main index build
# -------------------------------------------------------
def build_semantic_index() -> dict:
    records = _read_orders_from_sqlite()

    if not records:
        raise ValueError("No orders found in SQLite. Cannot build semantic index.")

    rank_sets = _build_rank_sets(records)

    today = datetime.today().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    root = Path(SEMANTIC_INDEX_ROOT)
    root.mkdir(parents=True, exist_ok=True)

    target_slot = _get_inactive_slot()
    target_dir = _slot_dir(target_slot)
    target_dir.mkdir(parents=True, exist_ok=True)

    texts: list[str] = []
    metadata: list[dict] = []

    for row in records:
        (
            text,
            recency_value,
            monetary_value,
            recency_monetary_value,
            amount_bucket,
            date_bucket,
        ) = build_order_text(
            row=row,
            rank_sets=rank_sets,
            today=today,
        )

        texts.append(text)

        metadata.append(
            {
                "order_id": row.get("order_id"),
                "customer_id": row.get("customer_id"),
                "amount_usd": row.get("amount_usd"),
                "order_date": row.get("order_date"),
                "original_currency": row.get("original_currency"),

                # New rank/business-rule semantic attributes
                "recency_value": recency_value,
                "monetary_value": monetary_value,
                "recency_monetary_value": recency_monetary_value,

                # Compatibility with existing semantic search service
                "amount_bucket": amount_bucket,
                "date_bucket": date_bucket,

                # Embedded text
                "text": text,
            }
        )

    # ---------------------------------------------------
    # SentenceTransformer embeddings
    # ---------------------------------------------------
    embedder = EmbeddingProvider(EMBEDDING_MODEL_NAME)
    embeddings = embedder.embed_texts(texts).astype(np.float32)

    if embeddings.ndim != 2:
        raise ValueError("Embedding output is not a 2D matrix.")

    # ---------------------------------------------------
    # Normalize for cosine similarity
    # FAISS IndexFlatIP + normalized vectors = cosine similarity
    # ---------------------------------------------------
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]

    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    index_version = str(int(time.time()))

    tmp_index_path = target_dir / "orders.faiss.tmp"
    tmp_metadata_path = target_dir / "metadata.json.tmp"
    tmp_manifest_path = target_dir / "manifest.json.tmp"

    final_index_path = target_dir / "orders.faiss"
    final_metadata_path = target_dir / "metadata.json"
    final_manifest_path = target_dir / "manifest.json"

    faiss.write_index(index, str(tmp_index_path))

    with tmp_metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    manifest = {
        "index_version": index_version,
        "active_slot": target_slot,
        "documents_indexed": len(metadata),
        "embedding_model": EMBEDDING_MODEL_NAME,
        "embedding_dimension": int(dim),
        "index_dir": str(target_dir),
        "note": (
            "Rank-based Recency_Value and Monetary_Value + "
            "today-based Recency_Monetary_Value + "
            "SentenceTransformer embeddings + cosine(IndexFlatIP)."
        ),
        "rank_rules": {
            "rank_window_size": RANK_WINDOW_SIZE,
            "recency_value": {
                "recent": "latest 10 records by order_date",
                "old": "oldest 10 records by order_date",
                "normal_recency": "all other records",
            },
            "monetary_value": {
                "expensive": "top 10 records by amount_usd",
                "cheap": "bottom 10 records by amount_usd",
                "medium_value": "all other records",
            },
        },
        "recency_monetary_rules": {
            "reference": "today",
            "index_build_date": today.strftime("%Y-%m-%d"),
            "recent_days": RECENT_DAYS,
            "old_days": OLD_DAYS,
            "expensive_threshold": EXPENSIVE_AMOUNT_THRESHOLD,
            "cheap_threshold": CHEAP_AMOUNT_THRESHOLD,
            "labels": [
                "recent_expensive",
                "recent_cheap",
                "old_expensive",
                "old_cheap",
                "neutral_combo",
            ],
        },
    }

    with tmp_manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # ---------------------------------------------------
    # Atomic replace within inactive slot
    # ---------------------------------------------------
    os.replace(tmp_index_path, final_index_path)
    os.replace(tmp_metadata_path, final_metadata_path)
    os.replace(tmp_manifest_path, final_manifest_path)

    # ---------------------------------------------------
    # Update active pointer only after index files are complete
    # ---------------------------------------------------
    active_pointer = {
        "active_slot": target_slot,
        "active_index_dir": str(target_dir),
        "index_version": index_version,
    }

    active_file = Path(SEMANTIC_ACTIVE_INDEX_FILE)
    active_file.parent.mkdir(parents=True, exist_ok=True)

    tmp_active_file = active_file.with_suffix(".json.tmp")

    with tmp_active_file.open("w", encoding="utf-8") as f:
        json.dump(active_pointer, f, ensure_ascii=False, indent=2)

    os.replace(tmp_active_file, active_file)

    return {
        "documents_indexed": len(metadata),
        "embedding_model": EMBEDDING_MODEL_NAME,
        "embedding_dimension": int(dim),
        "index_version": index_version,
        "active_slot": target_slot,
        "active_index_dir": str(target_dir),
    }