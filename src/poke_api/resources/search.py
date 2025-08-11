"""Search resource providing top-level search convenience methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .._types import NamedAPIResource, NamedAPIResourceList

if TYPE_CHECKING:
    from .._client import AsyncPoke, Poke


class SearchResource:
    """Top-level search resource with direct search implementation."""

    def __init__(self, client: Poke) -> None:
        self._client = client

    def pokemon(
        self,
        *,
        name_prefix: Optional[str] = None,
        type: Optional[str] = None,
        ability: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> NamedAPIResourceList:
        """Search Pokemon with multiple filters."""
        # 1) Start from the full list as a base (get all Pokemon names)
        base = self._client.pokemon._get_json("/pokemon?limit=10000")
        names = {r["name"] for r in base.get("results", [])}

        # 2) Intersect by type if provided
        if type:
            type_data = self._client.pokemon._get_json(f"/type/{type}")
            type_names = {p["pokemon"]["name"] for p in type_data.get("pokemon", [])}
            names &= type_names

        # 3) Intersect by ability if provided
        if ability:
            ability_data = self._client.pokemon._get_json(f"/ability/{ability}")
            ability_names = {
                p["pokemon"]["name"] for p in ability_data.get("pokemon", [])
            }
            names &= ability_names

        # 4) Filter by name prefix if provided
        if name_prefix:
            prefix = name_prefix.lower()
            names = {n for n in names if n.startswith(prefix)}

        # 5) Paginate client-side
        ordered = sorted(names)
        window = ordered[offset : offset + limit]

        return NamedAPIResourceList(
            count=len(ordered),
            next=None,
            previous=None,
            results=[
                NamedAPIResource(name=n, url=f"{self._client.base_url}/pokemon/{n}")
                for n in window
            ],
        )

    def generation(
        self,
        *,
        name_prefix: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> NamedAPIResourceList:
        """Search generations with filters."""
        # Get all generations
        page = self._client.generation._get_json("/generation?limit=1000")
        items = [
            NamedAPIResource(name=r["name"], url=r["url"])
            for r in page.get("results", [])
        ]

        # Filter by name prefix if provided
        if name_prefix:
            prefix = name_prefix.lower()
            items = [r for r in items if r.name.lower().startswith(prefix)]

        # Filter by region if provided (requires hydrating generation data)
        if region:
            filtered = []
            for r in items:
                # Extract generation name/id from the item
                gen_id_or_name = r.name
                g = self._client.generation.get(
                    gen_id_or_name
                )  # Get full generation data
                if g.main_region.name.lower() == region.lower():
                    filtered.append(
                        NamedAPIResource(
                            name=g.name,
                            url=f"{self._client.base_url}/generation/{g.id}",
                        )
                    )
            items = filtered

        # Apply pagination
        total = len(items)
        items = items[offset : offset + limit]

        return NamedAPIResourceList(
            count=total, next=None, previous=None, results=items
        )


class AsyncSearchResource:
    """Top-level async search resource with direct search implementation."""

    def __init__(self, client: AsyncPoke) -> None:
        self._client = client

    async def pokemon(
        self,
        *,
        name_prefix: Optional[str] = None,
        type: Optional[str] = None,
        ability: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> NamedAPIResourceList:
        """Search Pokemon with multiple filters."""
        # 1) Start from the full list as a base (get all Pokemon names)
        base = await self._client.pokemon._get_json("/pokemon?limit=10000")
        names = {r["name"] for r in base.get("results", [])}

        # 2) Intersect by type if provided
        if type:
            type_data = await self._client.pokemon._get_json(f"/type/{type}")
            type_names = {p["pokemon"]["name"] for p in type_data.get("pokemon", [])}
            names &= type_names

        # 3) Intersect by ability if provided
        if ability:
            ability_data = await self._client.pokemon._get_json(f"/ability/{ability}")
            ability_names = {
                p["pokemon"]["name"] for p in ability_data.get("pokemon", [])
            }
            names &= ability_names

        # 4) Filter by name prefix if provided
        if name_prefix:
            prefix = name_prefix.lower()
            names = {n for n in names if n.startswith(prefix)}

        # 5) Paginate client-side
        ordered = sorted(names)
        window = ordered[offset : offset + limit]

        return NamedAPIResourceList(
            count=len(ordered),
            next=None,
            previous=None,
            results=[
                NamedAPIResource(name=n, url=f"{self._client.base_url}/pokemon/{n}")
                for n in window
            ],
        )

    async def generation(
        self,
        *,
        name_prefix: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> NamedAPIResourceList:
        """Search generations with filters."""
        # Get all generations
        page = await self._client.generation._get_json("/generation?limit=1000")
        items = [
            NamedAPIResource(name=r["name"], url=r["url"])
            for r in page.get("results", [])
        ]

        # Filter by name prefix if provided
        if name_prefix:
            prefix = name_prefix.lower()
            items = [r for r in items if r.name.lower().startswith(prefix)]

        # Filter by region if provided (requires hydrating generation data)
        if region:
            filtered = []
            for r in items:
                # Extract generation name/id from the item
                gen_id_or_name = r.name
                g = await self._client.generation.get(
                    gen_id_or_name
                )  # Get full generation data
                if g.main_region.name.lower() == region.lower():
                    filtered.append(
                        NamedAPIResource(
                            name=g.name,
                            url=f"{self._client.base_url}/generation/{g.id}",
                        )
                    )
            items = filtered

        # Apply pagination
        total = len(items)
        items = items[offset : offset + limit]

        return NamedAPIResourceList(
            count=total, next=None, previous=None, results=items
        )
