"""Base resource classes for PokeAPI resources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from cachetools import TTLCache

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

    def _get_json(self, path: str, **kwargs) -> dict[str, Any]:
        """Helper to make GET request and return JSON with caching."""
        # Extract cache control parameters
        use_cache = kwargs.pop("use_cache", True)
        cache_ttl = kwargs.pop("cache_ttl", None)  # None means use default TTL
        force_refresh = kwargs.pop("force_refresh", False)

        # Create cache key (include query params if any)
        cache_key = path
        if "params" in kwargs and kwargs["params"]:
            import urllib.parse

            query_string = urllib.parse.urlencode(kwargs["params"])
            cache_key = f"{path}?{query_string}"

        # If cache is disabled or force refresh, skip cache entirely
        if not use_cache or force_refresh:
            r = self._client._request(HTTPMethod.GET, path, **kwargs)
            return r.json()

        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Cache miss - make request
        r = self._client._request(HTTPMethod.GET, path, **kwargs)
        result = r.json()

        # Store in cache with custom TTL if specified
        if cache_ttl is not None:
            # For custom TTL, we need a new cache or temporary storage
            # For simplicity, we'll use the main cache but note this limitation
            # In production, you might want per-TTL cache instances
            self._cache[cache_key] = result
        else:
            # Use default cache TTL
            self._cache[cache_key] = result

        return result

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

        # Extract cache control parameters
        use_cache = kwargs.pop("use_cache", True)
        cache_ttl = kwargs.pop(  # noqa: F841
            "cache_ttl", None
        )  # Extracted for API compatibility, limited support
        force_refresh = kwargs.pop("force_refresh", False)

        # Construct the full URL for the lock key (including query params)
        full_url = self._client._join(path)
        if "params" in kwargs and kwargs["params"]:
            import urllib.parse

            query_string = urllib.parse.urlencode(kwargs["params"])
            full_url = f"{full_url}?{query_string}"

        # If cache is disabled or force refresh, skip cache and locking entirely
        if not use_cache or force_refresh:
            r = await self._client._request(HTTPMethod.GET, path, **kwargs)
            return r.json()

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
                # Note: custom cache_ttl is not fully supported in this implementation
                # as we use a single TTLCache instance. For full TTL support, we'd need
                # separate cache instances or a more sophisticated caching strategy
                self._cache[full_url] = result
                return result
            finally:
                # Clean up the lock to prevent memory leaks
                # Only remove if no other tasks are waiting for it
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
