#!/usr/bin/env python3
"""
List Pokemon with pagination.

Demonstrates basic Pokemon listing functionality.
"""

from poke_api import Poke


def main():
    """List first 5 Pokemon."""
    client = Poke()
    
    # Get first 5 Pokemon - demonstrates friendly PokemonList printing
    pokemon_list = client.pokemon.list(limit=5)
    
    print(f"Pokemon List: {pokemon_list}")
    print(f"Total Pokemon: {pokemon_list.count}")
    print(f"Next page: {pokemon_list.next}")
    
    print("\nFirst 5 Pokemon:")
    for pokemon_ref in pokemon_list.results:
        print(f"- {pokemon_ref.name}: {pokemon_ref.url}")
    
    print(f"\nList summary:\n{pokemon_list.summary()}")
    
    # Show detailed access to individual Pokemon
    print(f"\nFetching first Pokemon details...")
    first_pokemon = client.pokemon.get(1) 
    print(f"Bulbasaur: {first_pokemon}")


if __name__ == "__main__":
    main()