#!/usr/bin/env python3
"""
Get a Pokemon using the synchronous client.

Demonstrates basic Pokemon retrieval with pretty printed output.
"""

from poke_api import Poke


def main():
    """Get Pikachu and show basic information."""
    client = Poke()

    # Get Pikachu and print basic info
    pikachu = client.pokemon.get("pikachu")

    # Demonstrate the new friendly repr format
    print(f"Pokemon: {pikachu}")
    print(f"\nSummary:\n{pikachu.summary()}")
    print(f"\nType: {pikachu.types[0].type.name}")
    print(f"Ability: {pikachu.abilities[0].ability.name}")

    # Show full data is still available
    print("\nFull data access:")
    print(f"  .to_dict() -> {len(pikachu.to_dict())} keys")
    print(f"  .to_json() -> {len(pikachu.to_json())} chars")


if __name__ == "__main__":
    main()
