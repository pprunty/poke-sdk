#!/usr/bin/env python3
"""
Get generation data using the asynchronous client.

Demonstrates async generation retrieval with proper cleanup.
"""

import asyncio
from poke_api import AsyncPoke


async def main():
    """Get Generation II asynchronously and show basic information."""
    client = AsyncPoke()
    
    try:
        # Get Generation II and print basic info
        gen2 = await client.generation.get(2)
        print(f"Generation: {gen2.name}")
        print(f"ID: {gen2.id}")
        print(f"Main Region: {gen2.main_region.name}")
        print(f"Pokemon Species Count: {len(gen2.pokemon_species)}")
        
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())