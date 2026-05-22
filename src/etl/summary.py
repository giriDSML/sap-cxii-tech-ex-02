# Just a simple utility to format the summary report in a nice way for console output
#once the batch is executed 

def format_summary(summary: dict) -> str:
    lines = [
        "ETL Summary",
        "-----------",
        f"Input rows: {summary['input_rows']}",
        f"Dropped rows (missing order_id/customer_id): {summary['dropped_missing_ids']}",
        f"Dropped rows (invalid dates): {summary['dropped_invalid_dates']}",
        f"Missing/invalid amounts defaulted to 0: {summary['invalid_or_missing_amounts_defaulted_to_zero']}",
        f"Missing currency defaulted to USD: {summary['missing_currency_defaulted_to_usd']}",
        f"Unsupported currency rows dropped: {summary['unsupported_currency_rows_dropped']}",
        f"Output rows: {summary['output_rows']}",
    ]
    return "\n".join(lines)