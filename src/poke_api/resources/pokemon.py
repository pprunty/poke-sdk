from __future__ import annotations

from typing import Union, overload

from .._resource import BaseAsyncResource, BaseResource
from .._types import NamedAPIResource
from ..pagination import AsyncPage, Page
from ..types.pokemon import Pokemon, PokemonList


class PokemonResource(BaseResource[Pokemon]):
    """Synchronous Pokemon resource."""

    _ENDPOINT = "/pokemon"

    @overload
    def get(self, id_or_name: Union[str, int]) -> Pokemon:
        ...

    @overload
    def get(self, *, id: Union[str, int]) -> Pokemon:
        ...

    @overload
    def get(self, *, name: str) -> Pokemon:
        ...

    @overload
    def get(self, *, id_or_name: Union[str, int]) -> Pokemon:
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
    ) -> Pokemon:
        """Get a Pokemon by ID or name.

        Args:
            id_or_name: Pokemon ID or name (positional, for backward compatibility)
            id: Pokemon ID (keyword-only)
            name: Pokemon name (keyword-only)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Custom cache TTL in seconds (default: 60s)
            force_refresh: Force refresh from API, bypass cache (default: False)
            **kwargs: Additional parameters (timeout, retries, backoff)

        Examples:
            client.pokemon.get(1)                           # positional
            client.pokemon.get(id=1)                        # keyword ID
            client.pokemon.get(name="pikachu")              # keyword name
            client.pokemon.get(id_or_name="pikachu")        # explicit keyword
            client.pokemon.get("pikachu", force_refresh=True)  # bypass cache
            client.pokemon.get("pikachu", cache_ttl=300)       # 5min cache
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
        return Pokemon(**data)

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
        """List Pokemon with pagination and cache control.

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
        typed = PokemonList(**data)
        return Page(
            result=typed.results,
            count=typed.count,
            next=typed.next,
            previous=typed.previous,
            client=self._client,
            endpoint="pokemon",
            original_params={"limit": limit, "offset": offset},
        )


class AsyncPokemonResource(BaseAsyncResource[Pokemon]):
    """Asynchronous Pokemon resource."""

    _ENDPOINT = "/pokemon"

    @overload
    async def get(self, id_or_name: Union[str, int]) -> Pokemon:
        ...

    @overload
    async def get(self, *, id: Union[str, int]) -> Pokemon:
        ...

    @overload
    async def get(self, *, name: str) -> Pokemon:
        ...

    @overload
    async def get(self, *, id_or_name: Union[str, int]) -> Pokemon:
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
    ) -> Pokemon:
        """Get a Pokemon by ID or name.

        Args:
            id_or_name: Pokemon ID or name (positional, for backward compatibility)
            id: Pokemon ID (keyword-only)
            name: Pokemon name (keyword-only)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Custom cache TTL in seconds (default: 60s)
            force_refresh: Force refresh from API, bypass cache (default: False)
            **kwargs: Additional parameters (timeout, retries, backoff)

        Examples:
            await client.pokemon.get(1)                           # positional
            await client.pokemon.get(id=1)                        # keyword ID
            await client.pokemon.get(name="pikachu")              # keyword name
            await client.pokemon.get(id_or_name="pikachu")        # explicit keyword
            await client.pokemon.get("pikachu", force_refresh=True)  # bypass cache
            await client.pokemon.get("pikachu", cache_ttl=300)       # 5min cache
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
        return Pokemon(**data)

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
        """List Pokemon with pagination and cache control.

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
        typed = PokemonList(**data)
        return AsyncPage(
            result=typed.results,
            count=typed.count,
            next=typed.next,
            previous=typed.previous,
            client=self._client,
            endpoint="pokemon",
            original_params={"limit": limit, "offset": offset},
        )
