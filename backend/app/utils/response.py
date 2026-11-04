from typing import Any, Optional

from fastapi.responses import JSONResponse

from app.utils.object_id import json_safe


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=json_safe({"success": True, "message": message, "data": data}),
    )


def success_data(data: Any = None, message: str = "Success") -> dict:
    return json_safe({"success": True, "message": message, "data": data})


def error_response(message: str, errors: Optional[list] = None, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "errors": errors or []},
    )
