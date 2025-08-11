#!/usr/bin/env python3
"""
Search Pokemon using the synchronous client.

Demonstrates Pokemon search functionality with various filters.
"""

from poke_api import Poke


def main():
    """Search Pokemon with different filters."""
    client = Poke()
    
    # Search by type
    print("Ground-type Pokemon (first 5):")
    ground_pokemon = client.search.pokemon(type="ground", limit=5)
    for pokemon in ground_pokemon.results:
        print(f"  - {pokemon.name}")
    
    print(f"\nTotal ground-type Pokemon: {ground_pokemon.count}")
    
    # Search by ability  
    print("\nPokemon with Sand Veil ability (first 3):")
    sand_veil_pokemon = client.search.pokemon(ability="sand-veil", limit=3)
    for pokemon in sand_veil_pokemon.results:
        print(f"  - {pokemon.name}")
    
    # Combined search (type + ability)
    print("\nGround-type Pokemon with Sand Veil (all results):")
    combined = client.search.pokemon(type="ground", ability="sand-veil")
    for pokemon in combined.results:
        print(f"  - {pokemon.name}")


if __name__ == "__main__":
    main()