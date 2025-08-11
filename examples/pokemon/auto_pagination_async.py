#!/usr/bin/env python3
"""
Demonstrate auto-pagination async iteration over all Pokemon.

Shows how to iterate through all pages automatically with async for.
"""

import asyncio
from poke_api import AsyncPoke


async def main():
    """Demonstrate auto-pagination async iteration."""
    client = AsyncPoke()

    try:
        print("=== Auto-Pagination Async Demo ===")
        print("Iterating through first 10 Pokemon using async auto-pagination...")

        # Get first page with small limit to demonstrate pagination
        pokemon_pages = await client.pokemon.list(limit=3)

        # Auto-iterate through pages asynchronously
        count = 0
        async for pokemon in pokemon_pages:
            print(f"{count + 1:2d}. {pokemon.name}")
            count += 1

            # Limit demo to first 10 for readability
            if count >= 10:
                break

        print(
            f"\n✅ Successfully iterated through {count} Pokemon using async auto-pagination!"
        )
        print(
            "The async iterator automatically fetched multiple pages behind the scenes."
        )

        print("\n=== Async Collection Demo ===")
        print("Collecting first 7 Pokemon into a list asynchronously:")

        # Alternative approach: collect into list with limit
        pokemon_pages = await client.pokemon.list(
            limit=2
        )  # Small pages to force pagination
        all_pokemon = []

        async for pokemon in pokemon_pages:
            all_pokemon.append(pokemon)
            if len(all_pokemon) >= 7:
                break

        print(f"Collected {len(all_pokemon)} Pokemon:")
        for i, pokemon in enumerate(all_pokemon, 1):
            print(f"  {i}. {pokemon.name}")

    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
