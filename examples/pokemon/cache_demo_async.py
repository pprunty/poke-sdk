#!/usr/bin/env python3
"""
Demonstrate caching performance benefits with asynchronous client.

Shows how repeated async API calls are cached for better performance.
"""

import asyncio
import time
from poke_api import AsyncPoke


async def main():
    """Demonstrate async caching performance benefits."""
    client = AsyncPoke()
    
    print("=== Async Caching Performance Demo ===")
    
    try:
        # Test 1: Multiple concurrent requests to same endpoint
        print("\n1. Concurrent Request Caching:")
        
        start = time.time()
        # First batch - all hit API (but may benefit from HTTP connection pooling)
        tasks1 = [client.pokemon.get("charizard") for _ in range(3)]
        results1 = await asyncio.gather(*tasks1)
        time1 = time.time() - start
        print(f"   First 3 concurrent calls: {time1:.3f}s")
        
        start = time.time()
        # Second batch - all hit cache
        tasks2 = [client.pokemon.get("charizard") for _ in range(3)]
        results2 = await asyncio.gather(*tasks2)
        time2 = time.time() - start
        print(f"   Second 3 concurrent calls: {time2:.3f}s")
        print(f"   Cache speedup: {time1/time2:.0f}x faster!")
        
        # Verify all results are the same
        assert all(r.name == "charizard" for r in results1 + results2)
        
        # Test 2: Search with top-level alias caching
        print("\n2. Top-Level Search Caching:")
        
        start = time.time()
        water_pokemon1 = await client.search.pokemon(type="water", limit=4)
        time1 = time.time() - start
        print(f"   First search: {time1:.3f}s - Found {water_pokemon1.count} water Pokemon")
        
        start = time.time()
        water_pokemon2 = await client.search.pokemon(type="water", limit=4)
        time2 = time.time() - start
        print(f"   Second search: {time2:.3f}s - Found {water_pokemon2.count} water Pokemon")
        print(f"   Cache speedup: {time1/time2:.0f}x faster!")
        
        print(f"\n   First 4 water Pokemon:")
        for pokemon in water_pokemon1.results[:4]:
            print(f"   - {pokemon.name}")
        
        # Test 3: Mixed search operations benefit from shared cache
        print("\n3. Mixed Operations with Shared Cache:")
        
        start = time.time()
        # This will benefit from cached water-type data from previous search
        mixed_search = await client.pokemon.search(type="water", ability="swift-swim", limit=3)
        time3 = time.time() - start
        print(f"   Water + Swift Swim search: {time3:.3f}s")
        print(f"   Found {mixed_search.count} Pokemon with both water type and swift-swim")
        print("   (Benefits from previously cached water-type data)")
        
        print("\n✅ Async caching works great with concurrent operations!")
        print("   Cache is shared across all async operations on the same client.")
        
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())