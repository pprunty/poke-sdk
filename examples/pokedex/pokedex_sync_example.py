#!/usr/bin/env python3
"""
Sync version of basic Pokedex example showing:
1. Rankings for all Johto Pokemon 
2. Mewtwo details printed as JSON
"""

import json
from poke_api import Poke


def main():
    """Basic Pokedex functionality demo (sync version)."""

    client = Poke()

    print("🎯 Basic Pokedex Example (Sync)")
    print("=" * 35)

    # 1. Get rankings for all Johto Pokemon (Generation 2)
    print("\n📊 1. Johto Pokemon Rankings")
    print("-" * 25)

    # Get Johto rankings sorted by total base stats
    johto_rankings = client.pokedex.rankings(generation=2, sort_by="total")

    print("📋 Top 5 Johto Pokemon (by Total Base Stats):")
    print()

    for i, pokemon in enumerate(johto_rankings[:5], 1):
        print(
            f"{i}. {pokemon.name.title():<12} BST: {pokemon.total_base_stat:3d} Types: {'/'.join(pokemon.types).title()}"
        )

    print(f"\n📈 Total Johto Pokemon: {len(johto_rankings)}")

    # 2. Get Mewtwo details and print as JSON
    print("\n🧬 2. Mewtwo Details (JSON)")
    print("-" * 25)

    # Get detailed Mewtwo information from Generation 1
    mewtwo_detail = client.pokedex.detail(generation=1, number=150)

    # Convert to a clean JSON structure (simplified for sync example)
    mewtwo_json = {
        "name": mewtwo_detail.name,
        "national_no": mewtwo_detail.national_no,
        "classification": mewtwo_detail.classification,
        "types": mewtwo_detail.types,
        "height_m": mewtwo_detail.height_m,
        "weight_kg": mewtwo_detail.weight_kg,
        "capture_rate": mewtwo_detail.capture_rate,
        "base_happiness": mewtwo_detail.base_happiness,
        "growth_rate": mewtwo_detail.growth_rate,
        "weaknesses": [
            d.type for d in mewtwo_detail.damage_taken if d.multiplier > 1.0
        ],
        "resistances": [
            d.type
            for d in mewtwo_detail.damage_taken
            if d.multiplier < 1.0 and d.multiplier > 0
        ],
        "movepool_size": {
            "level_up": len(mewtwo_detail.level_up_moves),
            "tm_hm": len(mewtwo_detail.tm_hm_moves),
        },
        "evolution_chain": mewtwo_detail.evolution_chain,
    }

    # Print as formatted JSON
    print(json.dumps(mewtwo_json, indent=2, ensure_ascii=False))

    print("\n✅ Sync Example Complete!")
    print("💡 Demonstrates sync API usage with generation parameters")


if __name__ == "__main__":
    main()
