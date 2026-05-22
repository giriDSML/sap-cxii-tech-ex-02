REQUIRED_COLUMNS = {
    "order_id",
    "customer_id",
    "order_date",
    "amount",
    "currency",
}

SUPPORTED_CURRENCIES = {"USD", "EUR"}

FX_RATES_TO_USD = {
    "USD": 1.0,
    "EUR": 1.1,
}

DEFAULT_CURRENCY = "USD"
DEFAULT_AMOUNT = 0.0