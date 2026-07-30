import json
import time
from typing import Any

from app.core.config import settings

try:
    from redis import Redis
    from redis.exceptions import RedisError
except ImportError:  # pragma: no cover - fallback para ambientes sem dependencia instalada
    Redis = None
    RedisError = Exception

DASHBOARD_METRICS_CACHE_KEY = "dashboard:metricas"
DASHBOARD_METRICS_TTL_SECONDS = 60

_redis_client: Redis | None = None
_redis_retry_after = 0.0


def get_redis_client() -> Redis | None:
    global _redis_client, _redis_retry_after

    if Redis is None:
        return None

    if not settings.redis_url:
        return None

    if time.monotonic() < _redis_retry_after:
        return None

    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )

    try:
        _redis_client.ping()
    except RedisError:
        _redis_client = None
        _redis_retry_after = time.monotonic() + 30
        return None

    return _redis_client


def get_json_cache(key: str) -> dict[str, Any] | None:
    client = get_redis_client()
    if client is None:
        return None

    try:
        value = client.get(key)
    except RedisError:
        return None

    if not value:
        return None

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        delete_cache(key)
        return None


def set_json_cache(key: str, value: dict[str, Any], ttl_seconds: int) -> None:
    client = get_redis_client()
    if client is None:
        return

    try:
        client.setex(key, ttl_seconds, json.dumps(value))
    except RedisError:
        return


def delete_cache(*keys: str) -> None:
    client = get_redis_client()
    if client is None or not keys:
        return

    try:
        client.delete(*keys)
    except RedisError:
        return


def set_cache_key(key: str, value: str, ttl_seconds: int) -> bool:
    client = get_redis_client()
    if client is None:
        return False

    try:
        client.setex(key, ttl_seconds, value)
    except RedisError:
        return False
    return True


def cache_key_exists(key: str) -> bool:
    client = get_redis_client()
    if client is None:
        return False

    try:
        return bool(client.exists(key))
    except RedisError:
        return False
