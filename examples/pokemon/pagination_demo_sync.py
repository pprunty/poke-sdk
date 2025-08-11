#!/usr/bin/env python3
"""
Demonstrate pagination functionality with synchronous client.

Shows Stainless-style pagination controls for navigating through Pokemon lists.
"""

from poke_api import Poke


def main():
    """Demonstrate pagination controls and navigation."""
    client = Poke()

    print("=== Pokemon Pagination Demo ===")

    # Start with a small page size to demonstrate pagination
    print("\n1. Getting first page of Pokemon (limit=5):")
    first_page = client.pokemon.list(limit=5)

    print(f"Page info: {first_page}")
    print(f"Total Pokemon: {first_page.count}")
    print(f"Items on this page: {len(first_page.result)}")
    print(f"Has next page: {first_page.has_next_page()}")

    # Show items on first page
    print("\nPokemon on first page:")
    for pokemon in first_page.result:
        print(f"  - {pokemon}")

    # Navigate to next page
    if first_page.has_next_page():
        print("\n2. Getting next page info and navigating:")
        next_info = first_page.next_page_info()
        print(f"Next page parameters: {next_info}")

        # Get next page using built-in navigation
        second_page = first_page.get_next_page()
        print(f"\nSecond page: {second_page}")

        print("\nPokemon on second page:")
        for pokemon in second_page.result:
            print(f"  - {pokemon}")

        # Navigate to third page
        if second_page.has_next_page():
            print("\n3. Getting third page:")
            third_page = second_page.get_next_page()
            print(f"Third page: {third_page}")

            print("\nPokemon on third page:")
            for pokemon in third_page.result:
                print(f"  - {pokemon}")

            # Demonstrate going backwards
            if third_page.has_previous_page():
                print("\n4. Going back to previous page:")
                prev_info = third_page.previous_page_info()
                print(f"Previous page parameters: {prev_info}")

                back_page = third_page.get_previous_page()
                print(f"Back to page: {back_page}")

    print("\n=== Generation Pagination Demo ===")

    # Test with generations (smaller dataset)
    gen_page = client.generation.list(limit=3)
    print(f"\nGeneration page: {gen_page}")

    print("\nGenerations:")
    for generation in gen_page.result:
        print(f"  - {generation}")

    print("\n✅ Pagination demo completed!")
    print("\nKey features demonstrated:")
    print("  - Page[T] objects with navigation methods")
    print("  - .has_next_page() / .has_previous_page() checks")
    print("  - .next_page_info() / .previous_page_info() parameter extraction")
    print("  - .get_next_page() / .get_previous_page() automatic navigation")
    print("  - Friendly Page representations showing item counts")


if __name__ == "__main__":
    main()
