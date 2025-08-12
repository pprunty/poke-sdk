"""Generation resource implementation."""

from __future__ import annotations

from typing import Union, overload

from .._resource import BaseAsyncResource, BaseResource
from .._types import NamedAPIResource
from ..pagination import AsyncPage, Page
from ..types.generation import Generation, GenerationList


class GenerationResource(BaseResource[Generation]):
    """Synchronous Generation resource."""

    _ENDPOINT = "/generation"

    @overload
    def get(self, id_or_name: Union[str, int]) -> Generation:
        ...

    @overload
    def get(self, *, id: Union[str, int]) -> Generation:
        ...

    @overload
    def get(self, *, name: str) -> Generation:
        ...

    @overload
    def get(self, *, id_or_name: Union[str, int]) -> Generation:
        ...

    def get(
        self,
        id_or_name: Union[str, int] = None,
        *,
        id: Union[str, int] = None,
        name: str = None,
        use_cache: bool = True,
        cache_ttl: int = None,
        force_refresh: bool = False,
        **kwargs,
    ) -> Generation:
        """Get a generation by ID or name.

        Args:
            id_or_name: Generation ID or name (positional, for backward compatibility)
            id: Generation ID (keyword-only)
            name: Generation name (keyword-only)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Custom cache TTL in seconds (default: 60s)
            force_refresh: Force refresh from API, bypass cache (default: False)
            **kwargs: Additional parameters (timeout, retries, backoff)

        Examples:
            client.generation.get(1)                           # positional
            client.generation.get(id=1)                        # keyword ID
            client.generation.get(name="generation-i")         # keyword name
            client.generation.get(id_or_name="generation-i")   # explicit keyword
            client.generation.get("generation-i", force_refresh=True)  # bypass cache
            client.generation.get("generation-i", cache_ttl=300)       # 5min cache
        """
        # Determine which identifier to use
        identifier = None
        provided_params = sum(x is not None for x in [id_or_name, id, name])

        if provided_params != 1:
            raise ValueError(
                "Exactly one of 'id_or_name' (positional), 'id', 'name', or 'id_or_name' (keyword) must be provided"
            )

        if id_or_name is not None:
            identifier = id_or_name
        elif id is not None:
            identifier = id
        elif name is not None:
            identifier = name

        # Use _get_json for caching support
        data = self._get_json(
            f"{self._ENDPOINT}/{identifier}",
            use_cache=use_cache,
            cache_ttl=cache_ttl,
            force_refresh=force_refresh,
            **kwargs,
        )
        return Generation(**data)

    def list(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        use_cache: bool = True,
        cache_ttl: int = None,
        force_refresh: bool = False,
        **kwargs,
    ) -> Page[NamedAPIResource]:
        """List generations with pagination and cache control.

        Args:
            limit: Number of items per page (default: 20)
            offset: Number of items to skip (default: 0)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Custom cache TTL in seconds (default: 60s)
            force_refresh: Force refresh from API, bypass cache (default: False)
            **kwargs: Additional parameters (timeout, retries, backoff)
        """
        data = self._get_json(
            self._ENDPOINT,
            params={"limit": limit, "offset": offset},
            use_cache=use_cache,
            cache_ttl=cache_ttl,
            force_refresh=force_refresh,
            **kwargs,
        )
        typed = GenerationList(**data)
        return Page(
            result=typed.results,
            count=typed.count,
            next=typed.next,
            previous=typed.previous,
            client=self._client,
            endpoint="generation",
            original_params={"limit": limit, "offset": offset},
        )


class AsyncGenerationResource(BaseAsyncResource[Generation]):
    """Asynchronous Generation resource."""

    _ENDPOINT = "/generation"

    @overload
    async def get(self, id_or_name: Union[str, int]) -> Generation:
        ...

    @overload
    async def get(self, *, id: Union[str, int]) -> Generation:
        ...

    @overload
    async def get(self, *, name: str) -> Generation:
        ...

    @overload
    async def get(self, *, id_or_name: Union[str, int]) -> Generation:
        ...

    async def get(
        self,
        id_or_name: Union[str, int] = None,
        *,
        id: Union[str, int] = None,
        name: str = None,
        use_cache: bool = True,
        cache_ttl: int = None,
        force_refresh: bool = False,
        **kwargs,
    ) -> Generation:
        """Get a generation by ID or name.

        Args:
            id_or_name: Generation ID or name (positional, for backward compatibility)
            id: Generation ID (keyword-only)
            name: Generation name (keyword-only)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Custom cache TTL in seconds (default: 60s)
            force_refresh: Force refresh from API, bypass cache (default: False)
            **kwargs: Additional parameters (timeout, retries, backoff)

        Examples:
            await client.generation.get(1)                           # positional
            await client.generation.get(id=1)                        # keyword ID
            await client.generation.get(name="generation-i")         # keyword name
            await client.generation.get(id_or_name="generation-i")   # explicit keyword
            await client.generation.get("generation-i", force_refresh=True)  # bypass cache
            await client.generation.get("generation-i", cache_ttl=300)       # 5min cache
        """
        # Determine which identifier to use
        identifier = None
        provided_params = sum(x is not None for x in [id_or_name, id, name])

        if provided_params != 1:
            raise ValueError(
                "Exactly one of 'id_or_name' (positional), 'id', 'name', or 'id_or_name' (keyword) must be provided"
            )

        if id_or_name is not None:
            identifier = id_or_name
        elif id is not None:
            identifier = id
        elif name is not None:
            identifier = name

        data = await self._get_json(
            f"{self._ENDPOINT}/{identifier}",
            use_cache=use_cache,
            cache_ttl=cache_ttl,
            force_refresh=force_refresh,
            **kwargs,
        )
        return Generation(**data)

    async def list(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        use_cache: bool = True,
        cache_ttl: int = None,
        force_refresh: bool = False,
        **kwargs,
    ) -> AsyncPage[NamedAPIResource]:
        """List generations with pagination and cache control.

        Args:
            limit: Number of items per page (default: 20)
            offset: Number of items to skip (default: 0)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Custom cache TTL in seconds (default: 60s)
            force_refresh: Force refresh from API, bypass cache (default: False)
            **kwargs: Additional parameters (timeout, retries, backoff)
        """
        data = await self._get_json(
            self._ENDPOINT,
            params={"limit": limit, "offset": offset},
            use_cache=use_cache,
            cache_ttl=cache_ttl,
            force_refresh=force_refresh,
            **kwargs,
        )
        typed = GenerationList(**data)
        return AsyncPage(
            result=typed.results,
            count=typed.count,
            next=typed.next,
            previous=typed.previous,
            client=self._client,
            endpoint="generation",
            original_params={"limit": limit, "offset": offset},
        )
