#!/usr/bin/env python3
"""
List Pokemon with pagination.

Demonstrates basic Pokemon listing functionality.
"""

from poke_api import Poke


def main():
    """List first 5 Pokemon with pagination demo."""
    client = Poke()

    for pokemon in client.pokemon.list():  # Limit for demo
        # Do something with pokemon here
        print(pokemon)


if __name__ == "__main__":
    main()
