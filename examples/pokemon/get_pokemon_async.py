#!/usr/bin/env python3
"""
Asynchronous Pokemon retrieval example.

Demonstrates async Pokemon retrieval with proper resource management.
"""

import asyncio

from poke_api import AsyncPoke
from poke_api._exceptions import NotFoundError


async def main():
    """Get individual Pokemon asynchronously with strong typing."""
    print("🔗 Connecting to PokeAPI (async)...")
    client = AsyncPoke()

    try:
        # Example 1: Get Pokemon by ID
        print("\n⚡ Getting Pikachu by ID (async)...")
        pikachu = await client.pokemon.get(25)
        print(f"Pokemon: {pikachu.name} (#{pikachu.id})")
        print(f"Height: {pikachu.height}")
        print(f"Weight: {pikachu.weight}")
        print(f"Summary: {pikachu.summary()}")

        # Example 2: Get Pokemon by name
        print("\n🔥 Getting Arcanine by name (async)...")
        arcanine = await client.pokemon.get("arcanine")
        print(f"Pokemon: {arcanine.name} (#{arcanine.id})")
        print(f"Type: {arcanine.types[0].type.name}")

        # Example 3: Accessing top stats
        print(f"\n📊 {arcanine.name.title()} Top 3 Stats:")
        sorted_stats = sorted(arcanine.stats, key=lambda s: s.base_stat, reverse=True)
        for stat in sorted_stats[:3]:
            print(f"  {stat.stat.name}: {stat.base_stat}")

        # Example 4: Accessing moves (first few)
        print(f"\n⚔️ {arcanine.name.title()} Sample Moves:")
        for move in arcanine.moves[:5]:  # Just show first 5 moves
            if move.move:
                print(f"  - {move.move.name}")

        # Example 5: Error handling
        print("\n❌ Testing async error handling...")
        try:
            await client.pokemon.get("fake-pokemon-12345")
        except NotFoundError as e:
            print(f"Expected error: {e}")

        print("\n✅ Async Pokemon retrieval examples completed!")

    finally:
        # Always clean up async resources
        await client.aclose()
        print("🔒 Client closed.")


if __name__ == "__main__":
    asyncio.run(main())
