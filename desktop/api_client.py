"""HTTP client for the ReBuild FastAPI backend (MongoDB persistence)."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from backend_map import as_list


class ApiError(Exception):
    def __init__(self, message: str, status: Optional[int] = None) -> None:
        super().__init__(message)
        self.status = status


class ReBuildApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def load_tokens(self, access: Optional[str], refresh: Optional[str]) -> None:
        self.access_token = access
        self.refresh_token = refresh

    def _unwrap(self, body: Any) -> Any:
        if isinstance(body, dict) and "success" in body and "data" in body:
            if not body.get("success", True):
                raise ApiError(str(body.get("message") or "Request failed"))
            return body.get("data")
        return body

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        auth: bool = True,
    ) -> Any:
        url = f"{self.base_url}{path}"
        if params:
            q = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            if q:
                url = f"{url}?{q}"

        data_bytes = None
        headers = {"Accept": "application/json"}
        if json_body is not None:
            data_bytes = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return self._unwrap(json.loads(raw)) if raw else None
        except urllib.error.HTTPError as exc:
            message = f"HTTP {exc.code}"
            try:
                payload = json.loads(exc.read().decode("utf-8"))
                if isinstance(payload, dict):
                    message = str(payload.get("message") or message)
                    errors = payload.get("errors")
                    if isinstance(errors, list) and errors:
                        parts: List[str] = []
                        for err in errors:
                            if not isinstance(err, dict):
                                continue
                            loc = err.get("loc")
                            field = loc[-1] if isinstance(loc, list) and loc else ""
                            msg = str(err.get("msg") or "")
                            if field and field not in ("body",):
                                parts.append(f"{field}: {msg}")
                            elif msg:
                                parts.append(msg)
                        if parts:
                            detail = "; ".join(parts)
                            if message.lower() == "validation error":
                                message = detail
                            else:
                                message = f"{message} ({detail})"
            except (json.JSONDecodeError, OSError):
                pass
            raise ApiError(message, status=exc.code) from exc
        except urllib.error.URLError as exc:
            raise ApiError(
                "Cannot reach the API. Start the backend (python run.py) and check the URL."
            ) from exc

    def register_user(
        self, full_name: str, email: str, mobile_number: str, password: str
    ) -> Dict[str, Any]:
        data = self._request(
            "POST",
            "/auth/register",
            json_body={
                "full_name": full_name,
                "email": email,
                "mobile_number": mobile_number,
                "password": password,
            },
            auth=False,
        )
        self.access_token = data["access_token"]
        self.refresh_token = data.get("refresh_token")
        return data

    def create_company(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/companies", json_body=payload)

    def login(self, email: str, password: str) -> Dict[str, Any]:
        data = self._request(
            "POST",
            "/auth/login",
            json_body={"email": email, "password": password},
            auth=False,
        )
        self.access_token = data["access_token"]
        self.refresh_token = data.get("refresh_token")
        return data

    def me(self) -> Dict[str, Any]:
        return self._request("GET", "/auth/me")

    def logout(self) -> None:
        if self.access_token:
            try:
                self._request(
                    "POST",
                    "/auth/logout",
                    json_body={"refresh_token": self.refresh_token},
                )
            except ApiError:
                pass
        self.access_token = None
        self.refresh_token = None

    def list_categories(self) -> List[Dict[str, Any]]:
        return as_list(self._request("GET", "/categories", auth=False))

    def search_materials(self, **params: Any) -> List[Dict[str, Any]]:
        return as_list(self._request("GET", "/materials", params=params, auth=False))

    def my_listings(self) -> List[Dict[str, Any]]:
        return as_list(self._request("GET", "/materials/my-listings", params={"page_size": 100}))

    def create_material(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/materials", json_body=payload)
