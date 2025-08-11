#!/usr/bin/env python3
"""
Demonstrate async pagination functionality with asynchronous client.

Shows Stainless-style async pagination controls for navigating through Pokemon lists.
"""

import asyncio

from poke_api import AsyncPoke


async def main():
    """Demonstrate async pagination controls and navigation."""
    client = AsyncPoke()

    try:
        print("=== Async Pokemon Pagination Demo ===")

        # Start with a small page size to demonstrate pagination
        print("\n1. Getting first page of Pokemon (limit=4):")
        first_page = await client.pokemon.list(limit=4)

        print(f"Page info: {first_page}")
        print(f"Total Pokemon: {first_page.count}")
        print(f"Items on this page: {len(first_page.result)}")
        print(f"Has next page: {first_page.has_next_page()}")

        # Show items on first page
        print("\nPokemon on first page:")
        for pokemon in first_page.result:
            print(f"  - {pokemon.name}")

        # Navigate to next page
        if first_page.has_next_page():
            print("\n2. Getting next page info and navigating:")
            next_info = first_page.next_page_info()
            print(f"Next page parameters: {next_info}")

            # Get next page using built-in navigation
            second_page = await first_page.get_next_page()
            print(f"\nSecond page: {second_page}")

            print("\nPokemon on second page:")
            for pokemon in second_page.result:
                print(f"  - {pokemon.name}")

            # Navigate to third page
            if second_page.has_next_page():
                print("\n3. Getting third page:")
                third_page = await second_page.get_next_page()
                print(f"Third page: {third_page}")

                print("\nPokemon on third page:")
                for pokemon in third_page.result:
                    print(f"  - {pokemon.name}")

        print("\n=== Async Generation Pagination Demo ===")

        # Test with generations (smaller dataset)
        gen_page = await client.generation.list(limit=2)
        print(f"\nGeneration page: {gen_page}")

        print("\nGenerations:")
        for generation in gen_page.result:
            print(f"  - {generation.name}")

        # Navigate to next generation page
        if gen_page.has_next_page():
            next_gen_page = await gen_page.get_next_page()
            print(f"\nNext generation page: {next_gen_page}")
            print("Next generations:")
            for generation in next_gen_page.result:
                print(f"  - {generation.name}")

        print("\n✅ Async pagination demo completed!")
        print("\nKey async features demonstrated:")
        print("  - AsyncPage[T] objects with async navigation methods")
        print("  - await page.get_next_page() / await page.get_previous_page()")
        print("  - Same pagination info extraction as sync version")
        print("  - Proper async/await resource management")

    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
