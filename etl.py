import argparse
from pathlib import Path

from src.etl.extract import load_csv
from src.etl.transform import transform_orders
from src.etl.load import upsert_orders
from src.etl.versioning import write_dataset_version
from src.etl.summary import format_summary
from src.db_layer.sqlite_client import get_connection
from src.db_layer.schema_manager import ensure_schema

import json
import urllib.request
import urllib.error

from src.search.index_builder import build_semantic_index
from src.config import SEMANTIC_RELOAD_URL



DEFAULT_DB_PATH = "db/orders.db"
DEFAULT_SCHEMA_PATH = "db/schema.sql"
DEFAULT_METADATA_PATH = "indexes/metadata.json"


def run_load(csv_path: str) -> None:
    df_raw = load_csv(csv_path)
    df_clean, summary = transform_orders(df_raw)

    Path("db").mkdir(parents=True, exist_ok=True)
    Path("indexes").mkdir(parents=True, exist_ok=True)

    conn = get_connection(DEFAULT_DB_PATH)
    try:
        ensure_schema(conn, DEFAULT_SCHEMA_PATH)
        loaded_count = upsert_orders(conn, df_clean)
   
    finally:
        conn.close()

    write_dataset_version(DEFAULT_METADATA_PATH, loaded_count)

    print(format_summary(summary))
    print(f"\nLoaded rows into SQLite: {loaded_count}")
    print(f"Database path: {DEFAULT_DB_PATH}")
    print(f"Metadata path: {DEFAULT_METADATA_PATH}")

    
  # -------------------------------------------------------
    #  NEW: Build semantic index (Part 4b)
    # -------------------------------------------------------

    # STEP 1 — Build index
    print("\n Building semantic index...")
    build_result = build_semantic_index()
    print("Semantic index built:", build_result)

    # STEP 2 — Notify API (THIS IS WHAT YOU ASKED)
    print("\nNotifying API to reload semantic index...")
    notify_api_to_reload_semantic_index()




def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Order ETL pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    load_parser = subparsers.add_parser("load", help="Load and process a CSV file")
    load_parser.add_argument("csv_path", help="Path to input CSV file")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "load":
        run_load(args.csv_path)


def notify_api_to_reload_semantic_index():
    req = urllib.request.Request(
        SEMANTIC_RELOAD_URL,
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            body = response.read().decode("utf-8")
            print("✅ API reload response:", body)

    except urllib.error.URLError as e:
        print(
            "Semantic index rebuilt but API reload failed. "
            "If API is not running, it will load on next startup."
        )
        print("Error:", e)

if __name__ == "__main__":
    main()