from pathlib import Path
import shutil

paths_to_delete = [
    Path("db/orders.db"),
    Path("artifacts/semantic_index"),
]

for path in paths_to_delete:
    if path.is_file():
        path.unlink()
        print(f"Deleted file: {path}")
    elif path.is_dir():
        shutil.rmtree(path)
        print(f"Deleted directory: {path}")
    else:
        print(f"Not found, skipped: {path}")

Path("db").mkdir(parents=True, exist_ok=True)
Path("artifacts/semantic_index").mkdir(parents=True, exist_ok=True)

print("Cleanup completed.")