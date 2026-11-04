from typing import Any, Dict, Optional

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def pagination_params(page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Dict[str, int]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
    skip = (page - 1) * page_size
    return {"page": page, "page_size": page_size, "skip": skip, "limit": page_size}


def paginated_meta(total: int, page: int, page_size: int) -> Dict[str, Any]:
    pages = (total + page_size - 1) // page_size if page_size else 0
    return {"total": total, "page": page, "page_size": page_size, "pages": pages}


def sort_param(sort_by: Optional[str], sort_order: str = "desc") -> tuple:
    direction = -1 if sort_order.lower() == "desc" else 1
    allowed = {
        "created_at": "created_at",
        "updated_at": "updated_at",
        "expected_price": "expected_price",
        "available_quantity": "available_quantity",
        "matching_score": "matching_score",
    }
    field = allowed.get(sort_by or "created_at", "created_at")
    return field, direction
