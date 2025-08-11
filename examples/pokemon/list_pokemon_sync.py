#!/usr/bin/env python3
"""
List Pokemon with pagination.

Demonstrates basic Pokemon listing functionality.
"""

from poke_api import Poke


def main():
    """List first 5 Pokemon with pagination demo."""
    client = Poke()

    # Get first 5 Pokemon - now returns Page[NamedAPIResource]
    pokemon_page = client.pokemon.list(limit=5)

    print(f"Pokemon Page: {pokemon_page}")
    print(f"Total Pokemon: {pokemon_page.count}")
    print(f"Has next page: {pokemon_page.has_next_page()}")

    print("\nFirst 5 Pokemon:")
    for pokemon_ref in pokemon_page.result:
        print(f"- {pokemon_ref.name}: {pokemon_ref.url}")

    # Demonstrate pagination navigation
    if pokemon_page.has_next_page():
        print(f"\nNext page info: {pokemon_page.next_page_info()}")
        print("\nGetting next page...")
        next_page = pokemon_page.get_next_page()
        print(f"Next page: {next_page}")

        print("\nNext 5 Pokemon:")
        for pokemon_ref in next_page.result:
            print(f"- {pokemon_ref.name}")

    # Show detailed access to individual Pokemon
    print("\nFetching first Pokemon details...")
    first_pokemon = client.pokemon.get(1)
    print(f"Bulbasaur: {first_pokemon}")


if __name__ == "__main__":
    main()
