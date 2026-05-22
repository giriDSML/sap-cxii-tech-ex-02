#  Below piece of code is for version tracking of data set changes.


import json
from datetime import datetime, timezone
from pathlib import Path


def write_dataset_version(metadata_path: str, row_count: int) -> None:
    payload = {
        "dataset_version": datetime.now(timezone.utc).isoformat(),
        "row_count": row_count,
    }

    path = Path(metadata_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")