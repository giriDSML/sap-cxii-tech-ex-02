from pathlib import Path


def load_schema_sql(schema_path: str) -> str:
    path = Path(schema_path)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    return path.read_text(encoding="utf-8")


def ensure_schema(conn, schema_path: str) -> None:
    schema_sql = load_schema_sql(schema_path)
    conn.executescript(schema_sql)
    conn.commit()