from __future__ import annotations

from typing import Union, overload

from .._resource import BaseAsyncResource, BaseResource, HTTPMethod
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
    ) -> Pokemon:
        """Get a Pokemon by ID or name.

        Args:
            id_or_name: Pokemon ID or name (positional, for backward compatibility)
            id: Pokemon ID (keyword-only)
            name: Pokemon name (keyword-only)

        Examples:
            client.pokemon.get(1)                    # positional
            client.pokemon.get(id=1)                 # keyword ID
            client.pokemon.get(name="pikachu")       # keyword name
            client.pokemon.get(id_or_name="pikachu") # explicit keyword
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

        r = self._client._request(HTTPMethod.GET, f"{self._ENDPOINT}/{identifier}")
        data = r.json()
        return Pokemon(**data)

    def list(self, *, limit: int = 20, offset: int = 0) -> Page[NamedAPIResource]:
        r = self._client._request(
            HTTPMethod.GET, self._ENDPOINT, params={"limit": limit, "offset": offset}
        )
        data = r.json()
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
    ) -> Pokemon:
        """Get a Pokemon by ID or name.

        Args:
            id_or_name: Pokemon ID or name (positional, for backward compatibility)
            id: Pokemon ID (keyword-only)
            name: Pokemon name (keyword-only)

        Examples:
            await client.pokemon.get(1)                    # positional
            await client.pokemon.get(id=1)                 # keyword ID
            await client.pokemon.get(name="pikachu")       # keyword name
            await client.pokemon.get(id_or_name="pikachu") # explicit keyword
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

        data = await self._get_json(f"{self._ENDPOINT}/{identifier}")
        return Pokemon(**data)

    async def list(
        self, *, limit: int = 20, offset: int = 0
    ) -> AsyncPage[NamedAPIResource]:
        data = await self._get_json(
            self._ENDPOINT, params={"limit": limit, "offset": offset}
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
