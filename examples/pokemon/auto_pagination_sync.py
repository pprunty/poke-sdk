#!/usr/bin/env python3
"""
Demonstrate auto-pagination sync iteration over all Pokemon.

Shows how to iterate through all pages automatically without manual navigation.
"""

from poke_api import Poke


def main():
    """Demonstrate auto-pagination sync iteration."""
    client = Poke()

    print("=== Auto-Pagination Sync Demo ===")
    print("Iterating through first 10 Pokemon using auto-pagination...")

    # Get first page with small limit to demonstrate pagination
    pokemon_pages = client.pokemon.list(limit=3)

    # Auto-iterate through pages - this will automatically fetch more pages as needed
    count = 0
    for pokemon in pokemon_pages:
        print(f"{count + 1:2d}. {pokemon.name}")
        count += 1

        # Limit demo to first 10 for readability
        if count >= 10:
            break

    print(f"\n✅ Successfully iterated through {count} Pokemon using auto-pagination!")
    print("The iterator automatically fetched multiple pages behind the scenes.")

    print("\n=== Limited Collection Demo ===")
    print("Collecting first 7 Pokemon into a list:")

    # Alternative approach: collect into list with limit
    pokemon_pages = client.pokemon.list(limit=2)  # Small pages to force pagination
    all_pokemon = []

    for pokemon in pokemon_pages:
        all_pokemon.append(pokemon)
        if len(all_pokemon) >= 7:
            break

    print(f"Collected {len(all_pokemon)} Pokemon:")
    for i, pokemon in enumerate(all_pokemon, 1):
        print(f"  {i}. {pokemon.name}")


if __name__ == "__main__":
    main()
