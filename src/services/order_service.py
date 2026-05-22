import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

from src.config import DB_PATH
from src.db_layer.sqlite_client import get_connection


def get_orders_by_customer(customer_id: str) -> list[dict[str, Any]]:
    """
    Returns all orders for a given customer_id.
    """
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
                original_currency,
                updated_at
            FROM orders
            WHERE customer_id = ?
            ORDER BY order_date DESC
            """,
            (customer_id,),
        ).fetchall()

        return [dict(r) for r in rows]

    finally:
        conn.close()


def get_order_stats() -> dict[str, Any]:
    """
    Returns:
    - total_revenue: sum of all amount_usd
    - avg_order_value: average of amount_usd
    - orders_per_day: dict keyed by date with count
    """
    conn = get_connection(DB_PATH)

    try:
        # Total revenue and average
        row = conn.execute(
            """
            SELECT
                COALESCE(SUM(amount_usd), 0) AS total_revenue,
                COALESCE(AVG(amount_usd), 0) AS avg_order_value
            FROM orders
            """
        ).fetchone()

        total_revenue = round(float(row["total_revenue"]), 2)
        avg_order_value = round(float(row["avg_order_value"]), 2)

        # Orders per day
        day_rows = conn.execute(
            """
            SELECT
                order_date,
                COUNT(*) AS order_count
            FROM orders
            GROUP BY order_date
            ORDER BY order_date
            """
        ).fetchall()

        orders_per_day = {
            str(r["order_date"]): r["order_count"]
            for r in day_rows
        }

        return {
            "total_revenue": total_revenue,
            "avg_order_value": avg_order_value,
            "orders_per_day": orders_per_day,
        }

    finally:
        conn.close()


def get_recent_orders(days: int) -> list[dict[str, Any]]:
    """
    Returns all orders from the last N days.

    Uses SQLite date() function for date comparison.
    """
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
                original_currency,
                updated_at
            FROM orders
            WHERE order_date >= date('now', ?)
            ORDER BY order_date DESC
            """,
            (f"-{days} days",),
        ).fetchall()

        return [dict(r) for r in rows]

    finally:
        conn.close()