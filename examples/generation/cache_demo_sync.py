#!/usr/bin/env python3
"""
Demonstrate generation caching with synchronous client.

Shows caching benefits for generation-related API calls.
"""

import time
from poke_api import Poke


def main():
    """Demonstrate generation caching benefits."""
    client = Poke()
    
    print("=== Generation Caching Demo ===")
    
    # Test 1: Generation lookup caching
    print("\n1. Generation Lookup Caching:")
    
    start = time.time()
    gen1_first = client.generation.get(1)
    time1 = time.time() - start
    print(f"   First call: {time1:.3f}s - {gen1_first.name}")
    print(f"   Main region: {gen1_first.main_region.name}")
    print(f"   Pokemon species: {len(gen1_first.pokemon_species)}")
    
    start = time.time()
    gen1_second = client.generation.get(1)
    time2 = time.time() - start
    print(f"   Second call: {time2:.3f}s - {gen1_second.name}")
    print(f"   Cache speedup: {time1/time2:.0f}x faster!")
    
    # Test 2: Generation search caching
    print("\n2. Generation Search Caching:")
    
    start = time.time()
    kanto_gens1 = client.generation.search(region="kanto")
    time1 = time.time() - start
    print(f"   First search: {time1:.3f}s - Found {kanto_gens1.count} Kanto generations")
    
    start = time.time()
    kanto_gens2 = client.generation.search(region="kanto")
    time2 = time.time() - start
    print(f"   Second search: {time2:.3f}s - Found {kanto_gens2.count} Kanto generations")
    print(f"   Cache speedup: {time1/time2:.0f}x faster!")
    
    # Test 3: Multiple generation lookups benefit from cache
    print("\n3. Multiple Generation Lookups:")
    
    generations_to_check = [1, 2, 1, 3, 2, 1]  # Note the repeats
    
    start = time.time()
    for gen_id in generations_to_check:
        gen = client.generation.get(gen_id)
        print(f"   Generation {gen_id}: {gen.name} ({gen.main_region.name} region)")
    total_time = time.time() - start
    
    print(f"\n   Total time for 6 lookups (with repeats): {total_time:.3f}s")
    print("   Repeated calls were served from cache!")
    
    print("\n✅ Generation data is efficiently cached!")
    print("   Cache benefits all resource types in the SDK.")


if __name__ == "__main__":
    main()