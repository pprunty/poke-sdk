"""Base resource classes for PokeAPI resources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from cachetools import TTLCache, cachedmethod

if TYPE_CHECKING:
    from ._client import AsyncPoke, Poke

T = TypeVar("T")


class HTTPMethod:
    """HTTP method constants."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class BaseResource(ABC, Generic[T]):
    """Base synchronous resource class."""

    def __init__(self, client: Poke) -> None:
        self._client = client
        self._cache = TTLCache(maxsize=1024, ttl=60)

    @cachedmethod(lambda self: self._cache)
    def _get_json(self, path: str) -> dict[str, Any]:
        """Helper to make GET request and return JSON with caching."""
        r = self._client._request(HTTPMethod.GET, path)
        return r.json()

    @abstractmethod
    def get(self, id_or_name: int | str) -> T:
        """Get a single resource by ID or name."""
        pass

    @abstractmethod
    def list(self, *, limit: int = 20, offset: int = 0, **kwargs) -> dict[str, Any]:
        """List resources with pagination."""
        pass


class BaseAsyncResource(ABC, Generic[T]):
    """Base asynchronous resource class."""

    def __init__(self, client: AsyncPoke) -> None:
        self._client = client
        self._cache = TTLCache(maxsize=1024, ttl=60)

    async def _get_json(self, path: str, **kwargs) -> dict[str, Any]:
        """Helper to make GET request and return JSON with caching and de-duplication."""
        import asyncio

        # Construct the full URL for the lock key (including query params)
        full_url = self._client._join(path)
        if "params" in kwargs and kwargs["params"]:
            import urllib.parse

            query_string = urllib.parse.urlencode(kwargs["params"])
            full_url = f"{full_url}?{query_string}"

        # Get or create a lock for this specific URL
        lock = self._client._locks.setdefault(full_url, asyncio.Lock())

        async with lock:
            try:
                # Check cache first (double-checked locking pattern)
                if full_url in self._cache:
                    return self._cache[full_url]

                # Cache miss - make request
                r = await self._client._request(HTTPMethod.GET, path, **kwargs)
                result = r.json()

                # Store in cache using full URL as key
                self._cache[full_url] = result
                return result
            finally:
                # Clean up the lock to prevent memory leaks
                # Only remove if no other tasks are waiting for it
                # We need to check this more carefully since the lock might be released
                # but still in use by this current context
                try:
                    # Check if we're the last one using this lock
                    if full_url in self._client._locks:
                        # Use a small delay to ensure concurrent requests have had a chance
                        # to acquire the lock before we delete it
                        await asyncio.sleep(0)
                        if not lock.locked():
                            del self._client._locks[full_url]
                except Exception:
                    # If cleanup fails, it's not critical - just continue
                    pass

    @abstractmethod
    async def get(self, id_or_name: int | str) -> T:
        """Get a single resource by ID or name."""
        pass

    @abstractmethod
    async def list(
        self, *, limit: int = 20, offset: int = 0, **kwargs
    ) -> dict[str, Any]:
        """List resources with pagination."""
        pass
