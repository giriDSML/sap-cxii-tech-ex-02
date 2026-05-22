
from datetime import datetime, timezone
import pandas as pd

from src.etl.contracts import (
    REQUIRED_COLUMNS,
    SUPPORTED_CURRENCIES,
    FX_RATES_TO_USD,
    DEFAULT_CURRENCY,
    DEFAULT_AMOUNT,
)


#this function validates the schema of the DataFrame, ensuring all required columns are present
def validate_schema(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

# below function drops rows with missing or invalid business keys (order_id, customer_id)
# and returns the cleaned DataFrame along with the count of dropped rows

def _drop_missing_business_keys(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    before = len(df)
    df = df.copy()

    df["order_id"] = df["order_id"].where(df["order_id"].notna(), None)
    df["customer_id"] = df["customer_id"].where(df["customer_id"].notna(), None)

    df["order_id"] = df["order_id"].astype("string").str.strip()
    df["customer_id"] = df["customer_id"].astype("string").str.strip()

    df = df[
        df["order_id"].notna() &
        df["customer_id"].notna() &
        (df["order_id"] != "") &
        (df["customer_id"] != "")
    ].copy()

    dropped = before - len(df)
    return df, dropped

# Normalizes the order_date column to a consistent format (YYYY-MM-DD) and counts the 
# number of invalid dates that were dropped. It uses pandas' to_datetime function with 
# error coercion to handle invalid date formats gracefully.
def _normalize_dates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    parsed = pd.to_datetime(df["order_date"], errors="coerce")
    invalid_count = int(parsed.isna().sum())

    df = df.loc[parsed.notna()].copy()
    df["order_date"] = parsed.loc[parsed.notna()].dt.strftime("%Y-%m-%d")

    return df, invalid_count

#  This function normalizes the amount column by converting it to numeric values, handling 
# errors by coercing invalid entries to NaN. It also counts the number of invalid or
#  missing amounts and fills those with a default value (0.0) 

def _normalize_amounts(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    amounts = pd.to_numeric(df["amount"], errors="coerce")
    invalid_or_missing = int(amounts.isna().sum())

    df = df.copy()
    df["original_amount"] = amounts.fillna(DEFAULT_AMOUNT)

    return df, invalid_or_missing



# This function normalizes the currency column by converting it to uppercase strings,
# stripping whitespace, and handling missing or unsupported currencies. 
# It counts the number of   missing and unsupported currencies,  fills missing values 
# with a default currency (USD),    and drops rows with unsupported currencies. 
# The original currency is preserved in a new column for reference.            

def _normalize_currencies(df: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    df = df.copy()

    currency_series = df["currency"].astype("string").str.upper().str.strip()

    missing_mask = (
        df["currency"].isna() |
        currency_series.isna() |
        (currency_series == "") |
        (currency_series == "NAN")
    )
    missing_count = int(missing_mask.sum())

    currency_series.loc[missing_mask] = DEFAULT_CURRENCY

    unsupported_mask = ~currency_series.isin(SUPPORTED_CURRENCIES)
    unsupported_count = int(unsupported_mask.sum())

    df = df.loc[~unsupported_mask].copy()
    currency_series = currency_series.loc[~unsupported_mask]

    df["original_currency"] = currency_series

    return df, missing_count, unsupported_count



# This function converts the original amount to USD using predefined exchange rates.

def _convert_to_usd(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["amount_usd"] = df.apply(
        lambda row: float(row["original_amount"]) * FX_RATES_TO_USD[row["original_currency"]],
        axis=1
    )
    return df

# This function adds an updated_at timestamp to the DataFrame, 
# indicating when the data was last processed or transformed for audit and tracking purposes. The timestamp is in ISO 8601 format with UTC timezone.

def _add_updated_at(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["updated_at"] = datetime.now(timezone.utc).isoformat()
    return df


# The main ETL pipeline that orchestrates the entire data transformation process


def transform_orders(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    validate_schema(df)

    input_rows = len(df)

    df, dropped_missing_ids = _drop_missing_business_keys(df)
    df, dropped_invalid_dates = _normalize_dates(df)
    df, invalid_or_missing_amounts = _normalize_amounts(df)
    df, missing_currency_count, unsupported_currency_count = _normalize_currencies(df)
    df = _convert_to_usd(df)
    df = _add_updated_at(df)

    final_df = df[
        [
            "order_id",
            "customer_id",
            "order_date",
            "amount_usd",
            "original_amount",
            "original_currency",
            "updated_at",
        ]
    ].copy()

    summary = {
        "input_rows": input_rows,
        "dropped_missing_ids": dropped_missing_ids,
        "dropped_invalid_dates": dropped_invalid_dates,
        "invalid_or_missing_amounts_defaulted_to_zero": invalid_or_missing_amounts,
        "missing_currency_defaulted_to_usd": missing_currency_count,
        "unsupported_currency_rows_dropped": unsupported_currency_count,
        "output_rows": len(final_df),
    }

    return final_df, summary
