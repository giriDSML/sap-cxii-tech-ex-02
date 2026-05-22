import sqlite3
import pandas as pd


UPSERT_SQL = """
INSERT INTO orders (
    order_id,
    customer_id,
    order_date,
    amount_usd,
    original_amount,
    original_currency,
    updated_at
)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(order_id) DO UPDATE SET
    customer_id = excluded.customer_id,
    order_date = excluded.order_date,
    amount_usd = excluded.amount_usd,
    original_amount = excluded.original_amount,
    original_currency = excluded.original_currency,
    updated_at = excluded.updated_at;
"""


# for the assement insert has been used. In a real world scenario, 
#I would move to batch processing with chunked inserts or database-native bulk loaders (like PostgreSQL execute_values or COPY).

def upsert_orders(conn: sqlite3.Connection, df: pd.DataFrame) -> int:
    rows = [
        (
            str(row["order_id"]),
            str(row["customer_id"]),
            str(row["order_date"]),
            float(row["amount_usd"]),
            float(row["original_amount"]),
            str(row["original_currency"]),
            str(row["updated_at"]),
        )
        for _, row in df.iterrows()
    ]

    with conn:
        conn.executemany(UPSERT_SQL, rows)

    return len(rows)