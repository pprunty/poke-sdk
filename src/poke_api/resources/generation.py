"""Generation resource implementation."""

from __future__ import annotations
from typing import Dict, Any, Optional

from .._resource import BaseResource, BaseAsyncResource, HTTPMethod
from ..types.generation import Generation, GenerationList


class GenerationResource(BaseResource[Generation]):
    """Synchronous Generation resource."""
    
    _ENDPOINT = "/generation"

    def get(self, id_or_name) -> Generation:
        """Get a generation by ID or name."""
        r = self._client._request(HTTPMethod.GET, f"{self._ENDPOINT}/{id_or_name}")
        data = r.json()
        return Generation(**data)

    def list(self, *, limit: int = 20, offset: int = 0) -> GenerationList:
        """List generations with pagination."""
        r = self._client._request(
            HTTPMethod.GET, self._ENDPOINT, params={"limit": limit, "offset": offset}
        )
        data = r.json()
        return GenerationList(**data)



class AsyncGenerationResource(BaseAsyncResource[Generation]):
    """Asynchronous Generation resource."""
    
    _ENDPOINT = "/generation"

    async def get(self, id_or_name) -> Generation:
        """Get a generation by ID or name."""
        data = await self._get_json(f"{self._ENDPOINT}/{id_or_name}")
        return Generation(**data)

    async def list(self, *, limit: int = 20, offset: int = 0) -> GenerationList:
        """List generations with pagination."""
        data = await self._get_json(
            self._ENDPOINT, params={"limit": limit, "offset": offset}
        )
        return GenerationList(**data)

