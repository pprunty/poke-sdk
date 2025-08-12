#!/usr/bin/env python3
"""
Pokemon Expand Example

This example demonstrates how to use the expand() method to fetch detailed data
for referenced resources like moves, abilities, and species.

The expand() method resolves selected name/url references into full objects,
bounded by depth and max requests. It returns a dict copy of your model,
leaving the original model untouched.

Key Features:
- Non-invasive: Original models are never modified
- Path filtering: Target specific references like moves.move, species, abilities.ability
- Depth control: Control how deep the expansion goes
- Request budgeting: Prevent runaway API usage
- Async concurrency: Control parallel requests
- Automatic deduplication: Same URLs are only fetched once
- Cache integration: Uses existing client caching and retry logic
"""

import asyncio
import json
from poke_api import Poke, AsyncPoke


def sync_expand_example():
    """Synchronous expand example."""
    print("=== Synchronous Pokemon Expand Example ===\n")

    client = Poke()
    # Get a Pokemon (bulbasaur has many moves and abilities to expand)
    print("1. Fetching bulbasaur...")
    bulba = client.pokemon.get("bulbasaur")
    print(f"   Pokemon: {bulba.name} (ID: {bulba.id})")
    print(f"   Moves: {len(bulba.moves)} moves available")
    print(f"   Abilities: {len(bulba.abilities)} abilities available")
    print()

    # Expand the first few move references to get full move data
    print("2. Expanding first 3 moves...")
    expanded = client.expand(
        bulba,
        paths=["moves.move"],  # Only expand move references in the moves array
        depth=1,  # Don't go deeper than 1 level
        max_requests=10,  # Limit to 10 API calls
    )

    print("   Expanded moves:")
    for i, move_data in enumerate(expanded["moves"][:3]):
        move = move_data["move"]
        expanded_move = move.get("__expanded__", {})
        if expanded_move:
            print(
                f"     {i+1}. {expanded_move['name']} (Power: {expanded_move.get('power', 'N/A')}, "
                f"Accuracy: {expanded_move.get('accuracy', 'N/A')}, "
                f"PP: {expanded_move.get('pp', 'N/A')})"
            )
        else:
            print(f"     {i+1}. {move['name']} (not expanded)")
    print()

    # Expand abilities
    print("3. Expanding abilities...")
    expanded_abilities = client.expand(
        bulba, paths=["abilities.ability"], depth=1, max_requests=5
    )

    print("   Expanded abilities:")
    for ability_data in expanded_abilities["abilities"]:
        ability = ability_data["ability"]
        expanded_ability = ability.get("__expanded__", {})
        if expanded_ability:
            print(
                f"     - {expanded_ability['name']}: {expanded_ability.get('effect_entries', [{}])[0].get('effect', 'No description')[:100]}..."
            )
        else:
            print(f"     - {ability['name']} (not expanded)")
    print()

    # Show the structure of expanded data
    print("4. Data structure example:")
    first_move = expanded["moves"][:3][0]["move"]
    print(f"   Original move data: {first_move['name']} -> {first_move['url']}")
    if "__expanded__" in first_move:
        expanded_move = first_move["__expanded__"]
        print(
            f"   Expanded move data: {expanded_move['name']} (Power: {expanded_move.get('power', 'N/A')})"
        )
    print()


async def async_expand_example():
    """Asynchronous expand example with concurrency control."""
    print("=== Asynchronous Pokemon Expand Example ===\n")

    async with AsyncPoke() as client:
        # Get a Pokemon with many references
        print("1. Fetching mewtwo (has many moves and forms)...")
        mewtwo = await client.pokemon.get("mewtwo")
        print(f"   Pokemon: {mewtwo.name} (ID: {mewtwo.id})")
        print(f"   Moves: {len(mewtwo.moves)} moves available")
        print(f"   Forms: {len(mewtwo.forms)} forms available")
        print()

        # Expand moves with higher concurrency
        print("2. Expanding moves with concurrency=8...")
        expanded = await client.expand(
            mewtwo,
            paths=["moves.move"],
            depth=1,
            max_requests=20,  # More requests allowed
            concurrency=8,  # Higher concurrency for faster expansion
        )

        print("   Sample expanded moves:")
        for i, move_data in enumerate(expanded["moves"][:5]):
            move = move_data["move"]
            expanded_move = move.get("__expanded__", {})
            if expanded_move:
                print(
                    f"     {i+1}. {expanded_move['name']} - "
                    f"Type: {expanded_move.get('type', {}).get('name', 'N/A')}, "
                    f"Power: {expanded_move.get('power', 'N/A')}, "
                    f"Category: {expanded_move.get('damage_class', {}).get('name', 'N/A')}"
                )
            else:
                print(f"     {i+1}. {move['name']} (not expanded)")
        print()

        # Expand forms
        print("3. Expanding forms...")
        expanded_forms = await client.expand(
            mewtwo, paths=["forms"], depth=1, max_requests=10, concurrency=4
        )

        print("   Available forms:")
        for form_data in expanded_forms["forms"]:
            expanded_form = form_data.get("__expanded__", {})
            if expanded_form:
                form_names = expanded_form.get("form_names", [])
                form_name = (
                    form_names[0].get("name", "No name") if form_names else "No name"
                )
                print(f"     - {expanded_form['name']}: {form_name}")
            else:
                print(f"     - {form_data['name']} (not expanded)")
        print()

        # Demonstrate depth control
        print("4. Expanding moves with depth=2 (includes move type details)...")
        deep_expanded = await client.expand(
            mewtwo,
            paths=["moves.move.type"],  # Also expand the type of each move
            depth=2,  # Go 2 levels deep
            max_requests=15,
            concurrency=6,
        )

        print("   Deep expanded move (with type details):")
        first_move = deep_expanded["moves"][0]["move"]
        if "__expanded__" in first_move:
            move = first_move["__expanded__"]
            move_type = move.get("type", {})
            expanded_type = move_type.get("__expanded__", {})

            print(f"     Move: {move['name']}")
            print(f"       Type: {move_type['name']}")
            if expanded_type:
                print(
                    f"       Type details: {expanded_type.get('names', [{}])[0].get('name', 'No name')}"
                )
                print(
                    f"       Type color: {expanded_type.get('color', {}).get('name', 'N/A')}"
                )
        print()


def expand_with_paths_example():
    """Example showing different path filtering options."""
    print("=== Path Filtering Examples ===\n")

    client = Poke()
    # Get a Pokemon
    print("1. Fetching charizard...")
    charizard = client.pokemon.get("charizard")
    print(f"   Pokemon: {charizard.name}")
    print()

    # Expand multiple different paths
    print("2. Expanding multiple paths: moves.move, species, and abilities.ability...")
    expanded = client.expand(
        charizard,
        paths=[
            "moves.move",  # Expand move references
            "species",  # Expand species reference
            "abilities.ability",  # Expand ability references
        ],
        depth=1,
        max_requests=15,
    )

    print("   Expanded data summary:")

    # Check moves
    moves_count = len([m for m in expanded["moves"] if "__expanded__" in m["move"]])
    print(f"     - Moves expanded: {moves_count}/{len(expanded['moves'])}")

    # Check species
    species_expanded = "__expanded__" in expanded.get("species", {})
    print(f"     - Species expanded: {species_expanded}")

    # Check abilities
    abilities_count = len(
        [a for a in expanded["abilities"] if "__expanded__" in a["ability"]]
    )
    print(f"     - Abilities expanded: {abilities_count}/{len(expanded['abilities'])}")
    print()

    # Show species data if expanded
    if species_expanded:
        species = expanded["species"]
        expanded_species = species.get("__expanded__", {})
        print("   Species details:")
        print(f"     - Name: {expanded_species.get('name', 'N/A')}")
        print(f"     - Base happiness: {expanded_species.get('base_happiness', 'N/A')}")
        print(f"     - Capture rate: {expanded_species.get('capture_rate', 'N/A')}")
        print(
            f"     - Growth rate: {expanded_species.get('growth_rate', {}).get('name', 'N/A')}"
        )


def main():
    """Run all examples."""
    print("Pokemon Expand Examples")
    print("=" * 50)
    print()

    # Run sync example
    sync_expand_example()
    print()

    # Run path filtering example
    expand_with_paths_example()
    print()

    # Run async example
    print("Running async example...")
    asyncio.run(async_expand_example())

    print("\n" + "=" * 50)
    print("Expand examples completed!")
    print("\nKey takeaways:")
    print("- Use paths to target specific references")
    print("- Control depth to avoid excessive expansion")
    print("- Set max_requests to prevent runaway API usage")
    print("- Use concurrency for faster async expansion")
    print("- Original models are never modified")
    print("- Expanded data is stored under __expanded__ key")


if __name__ == "__main__":
    main()
