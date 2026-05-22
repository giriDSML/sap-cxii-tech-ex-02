from pathlib import Path
import pandas as pd


def load_csv(file_path: str) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a CSV file, got: {file_path}")

    return pd.read_csv(path)
