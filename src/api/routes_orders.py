from fastapi import APIRouter, HTTPException, Path, Query
from typing import Any

from src.services.order_service import (
    get_orders_by_customer,
    get_order_stats,
    get_recent_orders,
)


router = APIRouter(prefix="/orders", tags=["orders-query"])


# -------------------------------------------------------
# GET /orders/customer/{customer_id}
# -------------------------------------------------------
@router.get("/customer/{customer_id}")
def orders_by_customer(
    customer_id: str = Path(
        ...,
        min_length=1,
        description="Customer ID to look up orders for",
    ),
) -> list[dict[str, Any]]:
    """
    Returns all orders for a given customer.

    Example:
      GET /orders/customer/C128
    """
    try:
        orders = get_orders_by_customer(customer_id)

        if not orders:
            raise HTTPException(
                status_code=404,
                detail=f"No orders found for customer: {customer_id}",
            )

        return orders

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve orders: {str(e)}",
        )


# -------------------------------------------------------
# GET /orders/stats
# -------------------------------------------------------
@router.get("/stats")
def order_stats() -> dict[str, Any]:
    """
    Returns order statistics:
    - total_revenue: sum of all amount_usd
    - avg_order_value: average of amount_usd
    - orders_per_day: dict keyed by date

    Example response:
    {
      "total_revenue": 12345.67,
      "avg_order_value": 87.5,
      "orders_per_day": {
        "2020-01-01": 15,
        "2020-01-02": 20
      }
    }
    """
    try:
        return get_order_stats()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve order stats: {str(e)}",
        )


# -------------------------------------------------------
# GET /orders/recent?days=N
# -------------------------------------------------------
@router.get("/recent")
def recent_orders(
    days: int = Query(
        ...,
        ge=1,
        description="Number of days to look back",
    ),
) -> list[dict[str, Any]]:
    """
    Returns all orders from the last N days.

    Example:
      GET /orders/recent?days=30
    """
    try:
        orders = get_recent_orders(days)
        return orders

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve recent orders: {str(e)}",
        )