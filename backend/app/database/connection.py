from typing import Optional

from pymongo import AsyncMongoClient

from app.core.config import get_settings

_client: Optional[AsyncMongoClient] = None
_db = None


async def connect_to_mongo() -> None:
    global _client, _db
    settings = get_settings()
    _client = AsyncMongoClient(settings.mongodb_url)
    _db = _client[settings.mongodb_database]
    await _client.admin.command("ping")


async def close_mongo_connection() -> None:
    global _client, _db
    if _client:
        await _client.close()
    _client = None
    _db = None


def get_database():
    if _db is None:
        raise RuntimeError("Database is not initialized")
    return _db


def get_client() -> AsyncMongoClient:
    if _client is None:
        raise RuntimeError("Mongo client is not initialized")
    return _client
