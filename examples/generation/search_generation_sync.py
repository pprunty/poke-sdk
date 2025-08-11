#!/usr/bin/env python3
"""
Search generations using the synchronous client.

Demonstrates generation search functionality with region filtering.
"""

from poke_api import Poke


def main():
    """Search generations by region."""
    client = Poke()

    # Search generations by region
    print("Generations in Kanto region:")
    kanto_gens = client.search.generation(region="kanto")
    for gen in kanto_gens.results:
        print(f"  - {gen.name}")

    print(f"\nTotal generations in Kanto: {kanto_gens.count}")

    # Search with name prefix
    print("\nGenerations starting with 'generation-i':")
    gen_i = client.search.generation(name_prefix="generation-i")
    for gen in gen_i.results:
        print(f"  - {gen.name}")


if __name__ == "__main__":
    main()
