"""Local desktop config and saved API session (tokens)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

DESKTOP_DIR = Path(__file__).resolve().parent
DEFAULT_API_BASE = "http://127.0.0.1:8000/api/v1"
CONFIG_PATH = DESKTOP_DIR / "config.json"
SESSION_PATH = DESKTOP_DIR / "session.json"


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.is_file():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return {"api_base_url": DEFAULT_API_BASE}


def save_config(data: Dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_session() -> Optional[Dict[str, Any]]:
    if not SESSION_PATH.is_file():
        return None
    try:
        data = json.loads(SESSION_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def save_session(data: Optional[Dict[str, Any]]) -> None:
    if not data:
        if SESSION_PATH.is_file():
            SESSION_PATH.unlink(missing_ok=True)
        return
    SESSION_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
