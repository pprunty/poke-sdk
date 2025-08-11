#!/usr/bin/env python3
"""
Get generation data using the synchronous client.

Demonstrates basic generation retrieval with pretty printed output.
"""

from poke_api import Poke


def main():
    """Get Generation I and show basic information."""
    client = Poke()

    # Get Generation I - demonstrate friendly printing
    gen1 = client.generation.get(1)

    print(f"Generation: {gen1}")
    print(f"\nSummary:\n{gen1.summary()}")
    print(f"\nMain Region: {gen1.main_region}")
    print(f"Pokemon Species: {len(gen1.pokemon_species)} total")
    print(f"Moves: {len(gen1.moves)} total")

    # Show a few Pokemon species
    print("\nFirst 5 Pokemon species in Generation I:")
    for species in gen1.pokemon_species[:5]:
        print(f"  - {species}")

    # Full data access
    print("\nFull data access:")
    print(f"  .to_dict() -> {len(gen1.to_dict())} keys")
    print(f"  .to_json() -> {len(gen1.to_json())} chars")


if __name__ == "__main__":
    main()
