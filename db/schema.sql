CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    amount_usd REAL NOT NULL,
    original_amount REAL,
    original_currency TEXT,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id
ON orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_orders_order_date
ON orders(order_date);

CREATE INDEX IF NOT EXISTS idx_orders_customer_date
ON orders(customer_id, order_date);