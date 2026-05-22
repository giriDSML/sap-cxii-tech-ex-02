from fastapi import FastAPI

from src.api.routes_orders import router as orders_router
from src.api.routes_ai import router as ai_router
from src.search.index_builder import build_semantic_index
from src.search.semantic_search_service import semantic_store


app = FastAPI(
    title="Orders Service",
    version="1.0.0",
    description=(
        "Orders service with query API, NL-to-SQL, and semantic order search. "
        "Part 2 provides basic query endpoints. "
        "Part 4.1 provides natural-language-to-SQL over SQLite. "
        "Part 4.2 provides semantic order search using MiniLM embeddings and FAISS."
    ),
)


# -------------------------------------------------------
# Register API routers
# -------------------------------------------------------
# Part 2: basic query endpoints
app.include_router(orders_router)

# Part 4a + 4b: AI endpoints
app.include_router(ai_router)


# -------------------------------------------------------
# Startup: load or build semantic index
# -------------------------------------------------------
@app.on_event("startup")
def startup_load_or_build_semantic_index():
    """
    Startup behavior for Part 4b.

    Expected blue/green index layout:

        artifacts/
        └── semantic_index/
            ├── active_index.json
            ├── blue/
            │   ├── orders.faiss
            │   ├── metadata.json
            │   └── manifest.json
            └── green/
                ├── orders.faiss
                ├── metadata.json
                └── manifest.json

    Behavior:
    1. Try to load the currently active index using active_index.json.
    2. If no active index exists, build a new semantic index from SQLite.
    3. Load the newly built active index into API memory.

    Notes:
    - ETL rebuilds the inactive blue/green slot.
    - ETL updates active_index.json after the new slot is complete.
    - API does NOT read active_index.json on every search request.
    - API reads active_index.json only at startup or when the reload endpoint is called.
    """
    try:
        result = semantic_store.load_active_from_disk()
        print("Semantic index loaded from active pointer:", result)

    except FileNotFoundError:
        print("Semantic index not found. Building semantic index from SQLite...")

        build_result = build_semantic_index()
        print("Semantic index built:", build_result)

        result = semantic_store.load_active_from_disk()
        print("Semantic index loaded after build:", result)


# -------------------------------------------------------
# Health check
# -------------------------------------------------------
@app.get("/healthz")
def healthz():
    return "ok"