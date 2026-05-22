from fastapi import APIRouter, HTTPException, Header, Query

from src.api.models import AskRequest, AskResponse
from src.services.ask_service import answer_question
from src.ai.nl2sql import NL2SQLAnswerabilityError, NL2SQLValidationError
from src.ai.responsible_ai_guardrails import ResponsibleAIGuardrailError
from src.config import (
    DEFAULT_TENANT_ID,
    DEFAULT_TOP_K,
    MAX_TOP_K,
)
from src.search.semantic_search_service import semantic_store


router = APIRouter(prefix="/orders", tags=["orders"])


# -------------------------------------------------------
# Part 4a — NL-to-SQL endpoint
# -------------------------------------------------------
@router.post("/ask", response_model=AskResponse)
def ask_orders(
    request: AskRequest,
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
):
    """
    Natural language to SQL endpoint.
    """
    tenant_id = x_tenant_id or DEFAULT_TENANT_ID

    try:
        return answer_question(
            question=request.question,
            tenant_id=tenant_id,
        )

    except ResponsibleAIGuardrailError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except NL2SQLAnswerabilityError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except NL2SQLValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Generated SQL failed validation: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to answer question: {str(e)}",
        )


# -------------------------------------------------------
# Part 4b — Semantic order search endpoint
# -------------------------------------------------------
@router.get("/semantic_search")
def semantic_search_orders(
    q: str = Query(
        ...,
        min_length=2,
        description="Free-text semantic search query",
    ),
    top_k: int = Query(
        DEFAULT_TOP_K,
        ge=1,
        le=MAX_TOP_K,   # ✅ added limit validation
        description="Number of nearest orders to return",
    ),
):
    """
    Semantic order search endpoint.
    """
    try:
        return semantic_store.search(q, top_k)

    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {str(e)}",
        )


# -------------------------------------------------------
# Part 4b — Explicit semantic index reload endpoint
# -------------------------------------------------------
@router.post("/semantic_index/reload")
def reload_semantic_index():
    """
    Reloads active FAISS index into API memory.
    """
    try:
        result = semantic_store.load_active_from_disk()

        return {
            "status": "reloaded",
            **result,
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Index reload failed: {str(e)}",
        )


# -------------------------------------------------------
# Part 4b — Semantic index status endpoint
# -------------------------------------------------------
@router.get("/semantic_index/status")
def semantic_index_status():
    """
    Shows which semantic index is currently loaded.
    """
    try:
        return semantic_store.status()   # ✅ fixed method name

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch status: {str(e)}",
        )