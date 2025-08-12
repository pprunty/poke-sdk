#!/usr/bin/env python3
"""
Basic Pokedex example showing:
1. Rankings for all Johto Pokemon 
2. Mewtwo details printed as JSON
"""

import asyncio
import json
from poke_api import AsyncPoke


async def main():
    """Basic Pokedex functionality demo."""

    async with AsyncPoke() as client:
        # Get Johto rankings sorted by total base stats
        johto_rankings = await client.pokedex.rankings(
            generation=1
        )  # sort_by="total" default
        top5 = johto_rankings[:5]  # take first 5
        data = [p.to_dict() for p in top5]  # or p.model_dump(exclude_none=True)

        print(json.dumps(data, indent=2, ensure_ascii=False))

        # Get detailed Mewtwo information from Generation 4
        # You can use either number or name parameter
        mewtwo_detail = await client.pokedex.detail(generation=4, name="mewtwo")
        print(mewtwo_detail.to_json())


if __name__ == "__main__":
    asyncio.run(main())
