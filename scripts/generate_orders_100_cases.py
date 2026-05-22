from datetime import date, timedelta
import csv
from pathlib import Path


# ✅ Changed destination file
OUT_FILE = Path("data/order.csv")


def add_row(rows, order_id, customer_id, order_date, amount, currency="USD"):
    rows.append(
        {
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date.isoformat(),
            "amount": amount,
            "currency": currency,
        }
    )


def main():
    today = date.today()
    rows = []

    order_num = 5001

    # -------------------------------------------------------
    # CASE 1: recent_expensive
    # recent = within last 30 days from today
    # expensive = amount >= 300
    # Includes USD + EUR
    # -------------------------------------------------------
    recent_expensive_amounts = [
        (350, "USD"),
        (420, "EUR"),
        (500, "USD"),
        (650, "EUR"),
        (720, "USD"),
        (810, "EUR"),
        (900, "USD"),
        (1050, "EUR"),
        (1200, "USD"),
        (1500, "EUR"),
    ]

    for i, (amount, currency) in enumerate(recent_expensive_amounts):
        add_row(
            rows,
            str(order_num),
            f"C{order_num}",
            today - timedelta(days=i),
            amount,
            currency,
        )
        order_num += 1

    # -------------------------------------------------------
    # CASE 2: recent_cheap
    # recent = within last 30 days
    # cheap = amount <= 50
    # Use lower EUR values also, so even if converted, they remain cheap-ish
    # -------------------------------------------------------
    recent_cheap_amounts = [
        (5, "USD"),
        (8, "EUR"),
        (10, "USD"),
        (12, "EUR"),
        (15, "USD"),
        (18, "EUR"),
        (20, "USD"),
        (25, "EUR"),
        (30, "USD"),
        (35, "EUR"),
    ]

    for i, (amount, currency) in enumerate(recent_cheap_amounts):
        add_row(
            rows,
            str(order_num),
            f"C{order_num}",
            today - timedelta(days=10 + i),
            amount,
            currency,
        )
        order_num += 1

    # -------------------------------------------------------
    # CASE 3: recent but medium amount -> neutral_combo
    # recent = yes
    # amount neither cheap nor expensive
    # -------------------------------------------------------
    recent_medium_amounts = [
        (80, "USD"),
        (95, "EUR"),
        (110, "USD"),
        (125, "EUR"),
        (140, "USD"),
        (155, "EUR"),
        (170, "USD"),
        (185, "EUR"),
        (200, "USD"),
        (250, "EUR"),
    ]

    for i, (amount, currency) in enumerate(recent_medium_amounts):
        add_row(
            rows,
            str(order_num),
            f"C{order_num}",
            today - timedelta(days=20 + (i % 8)),
            amount,
            currency,
        )
        order_num += 1

    # -------------------------------------------------------
    # CASE 4: old_expensive
    # old = older than 1 year from today
    # expensive = amount >= 300
    # -------------------------------------------------------
    old_base = today - timedelta(days=420)

    old_expensive_amounts = [
        (320, "USD"),
        (380, "EUR"),
        (450, "USD"),
        (560, "EUR"),
        (700, "USD"),
        (850, "EUR"),
        (950, "USD"),
        (1100, "EUR"),
        (1300, "USD"),
        (1450, "EUR"),
    ]

    for i, (amount, currency) in enumerate(old_expensive_amounts):
        add_row(
            rows,
            str(order_num),
            f"C{order_num}",
            old_base - timedelta(days=i),
            amount,
            currency,
        )
        order_num += 1

    # -------------------------------------------------------
    # CASE 5: old_cheap
    # old = older than 1 year
    # cheap = amount <= 50
    # Includes USD + EUR
    # -------------------------------------------------------
    old_cheap_base = today - timedelta(days=470)

    old_cheap_amounts = [
        (5, "USD"),
        (8, "EUR"),
        (10, "USD"),
        (12, "EUR"),
        (15, "USD"),
        (18, "EUR"),
        (20, "USD"),
        (25, "EUR"),
        (30, "USD"),
        (35, "EUR"),
    ]

    for i, (amount, currency) in enumerate(old_cheap_amounts):
        add_row(
            rows,
            str(order_num),
            f"C{order_num}",
            old_cheap_base - timedelta(days=i),
            amount,
            currency,
        )
        order_num += 1

    # -------------------------------------------------------
    # CASE 6: old but medium amount -> neutral_combo
    # old = yes
    # amount neither cheap nor expensive
    # -------------------------------------------------------
    old_medium_base = today - timedelta(days=520)

    old_medium_amounts = [
        (75, "USD"),
        (90, "EUR"),
        (105, "USD"),
        (120, "EUR"),
        (135, "USD"),
        (150, "EUR"),
        (175, "USD"),
        (200, "EUR"),
        (225, "USD"),
        (260, "EUR"),
    ]

    for i, (amount, currency) in enumerate(old_medium_amounts):
        add_row(
            rows,
            str(order_num),
            f"C{order_num}",
            old_medium_base - timedelta(days=i),
            amount,
            currency,
        )
        order_num += 1

    # -------------------------------------------------------
    # CASE 7: normal date + medium amount -> neutral_combo
    # not recent, not old
    # date around today - 100 days
    # 40 rows
    # -------------------------------------------------------
    normal_base = today - timedelta(days=100)

    for i in range(40):
        amount = 100 + (i * 4)  # 100 to 256
        currency = "USD" if i % 2 == 0 else "EUR"

        add_row(
            rows,
            str(order_num),
            f"C{order_num}",
            normal_base - timedelta(days=i),
            amount,
            currency,
        )
        order_num += 1

    # -------------------------------------------------------
    # Safety check
    # -------------------------------------------------------
    assert len(rows) == 100, f"Expected 100 rows, got {len(rows)}"

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "order_id",
                "customer_id",
                "order_date",
                "amount",
                "currency",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows at {OUT_FILE}")
    print(f"Today used for generation: {today.isoformat()}")
    print("Currencies included: USD, EUR")


if __name__ == "__main__":
    main()