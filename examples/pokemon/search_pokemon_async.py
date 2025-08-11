#!/usr/bin/env python3
"""
Search Pokemon using the asynchronous client.

Demonstrates async Pokemon search functionality with various filters.
"""

import asyncio

from poke_api import AsyncPoke


async def main():
    """Search Pokemon with different filters asynchronously."""
    client = AsyncPoke()

    try:
        # Search by type - demonstrate friendly printing of search results
        print("Fire-type Pokemon search:")
        fire_pokemon = await client.search.pokemon(type="fire", limit=5)
        print(f"Search results: {fire_pokemon}")

        print("\nFirst 5 fire-type Pokemon:")
        for pokemon in fire_pokemon.results:
            print(f"  - {pokemon}")

        # Get full details for one Pokemon to show rich representation
        print(f"\nFetching details for {fire_pokemon.results[0].name}:")
        detailed_pokemon = await client.pokemon.get(fire_pokemon.results[0].name)
        print(f"Full Pokemon: {detailed_pokemon}")
        print(f"Summary:\n{detailed_pokemon.summary()}")

        # Show data access methods
        print("\nData methods available:")
        print(f"  Search results: {len(fire_pokemon.to_dict())} keys")
        print(f"  Pokemon details: {len(detailed_pokemon.to_dict())} keys")

    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
