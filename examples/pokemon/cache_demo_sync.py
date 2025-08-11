#!/usr/bin/env python3
"""
Demonstrate caching performance benefits with synchronous client.

Shows how repeated API calls are cached for better performance.
"""

import time
from poke_api import Poke


def main():
    """Demonstrate caching performance benefits."""
    client = Poke()
    
    print("=== Caching Performance Demo ===")
    
    # Test 1: Single Pokemon lookup caching
    print("\n1. Pokemon Lookup Caching:")
    
    # First call - hits API
    start = time.time()
    pikachu1 = client.pokemon.get("pikachu")
    time1 = time.time() - start
    print(f"   First call: {time1:.3f}s")
    print(f"   Result: {pikachu1}")
    
    # Second call - hits cache
    start = time.time()
    pikachu2 = client.pokemon.get("pikachu")
    time2 = time.time() - start
    print(f"   Second call: {time2:.3f}s")
    print(f"   Same result: {pikachu2}")
    print(f"   Cache speedup: {time1/time2:.0f}x faster!")
    
    # Test 2: Search operation caching
    print("\n2. Search Operation Caching:")
    
    # First search - hits multiple API endpoints
    start = time.time()
    fire_pokemon1 = client.pokemon.search(type="fire", limit=5)
    time1 = time.time() - start
    print(f"   First search: {time1:.3f}s - Found {fire_pokemon1.count} fire Pokemon")
    
    # Second search - uses cached endpoint data
    start = time.time()
    fire_pokemon2 = client.pokemon.search(type="fire", limit=5)
    time2 = time.time() - start
    print(f"   Second search: {time2:.3f}s - Found {fire_pokemon2.count} fire Pokemon")
    print(f"   Cache speedup: {time1/time2:.0f}x faster!")
    
    # Test 3: Combined search benefits even more from caching
    print("\n3. Complex Search Caching:")
    
    # Combined search uses multiple cached endpoints
    start = time.time()
    ground_sand_veil = client.pokemon.search(type="ground", ability="sand-veil")
    time3 = time.time() - start
    print(f"   Combined search: {time3:.3f}s - Found {ground_sand_veil.count} matches")
    print(f"   (Benefits from cached type and ability data)")
    
    print(f"\n   First 3 ground+sand-veil Pokemon:")
    for pokemon in ground_sand_veil.results[:3]:
        print(f"   - {pokemon}")
    
    print(f"\n   Search result summary:")
    print(f"   {ground_sand_veil.summary()}")
    
    print("\n✅ Caching improves performance significantly!")
    print("   Note: Cache TTL is 60 seconds, after which fresh data is fetched.")


if __name__ == "__main__":
    main()