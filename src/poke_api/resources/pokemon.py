from __future__ import annotations
from typing import Any, Dict, Optional

from .._resource import BaseResource, BaseAsyncResource, HTTPMethod
from .._types import NamedAPIResourceList, NamedAPIResource
from ..types.pokemon import Pokemon, PokemonList


class PokemonResource(BaseResource[Pokemon]):
    """Synchronous Pokemon resource."""
    
    _ENDPOINT = "/pokemon"

    def get(self, id_or_name) -> Pokemon:
        """Get a Pokemon by ID or name."""
        r = self._client._request(HTTPMethod.GET, f"{self._ENDPOINT}/{id_or_name}")
        data = r.json()
        return Pokemon(**data)

    def list(self, *, limit: int = 20, offset: int = 0) -> PokemonList:
        r = self._client._request(
            HTTPMethod.GET, self._ENDPOINT, params={"limit": limit, "offset": offset}
        )
        data = r.json()
        return PokemonList(**data)



class AsyncPokemonResource(BaseAsyncResource[Pokemon]):
    """Asynchronous Pokemon resource."""
    
    _ENDPOINT = "/pokemon"

    async def get(self, id_or_name) -> Pokemon:
        """Get a Pokemon by ID or name."""
        data = await self._get_json(f"{self._ENDPOINT}/{id_or_name}")
        return Pokemon(**data)

    async def list(self, *, limit: int = 20, offset: int = 0) -> PokemonList:
        data = await self._get_json(
            self._ENDPOINT, params={"limit": limit, "offset": offset}
        )
        return PokemonList(**data)

