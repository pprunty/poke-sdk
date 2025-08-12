"""Tests for Pokedex detail view functionality."""

import pytest
import respx
from httpx import Response

from poke_api import AsyncPoke, Poke

# Mock data
POKEDEX_DATA = {
    "pokemon_entries": [
        {
            "entry_number": 150,
            "pokemon_species": {
                "name": "mewtwo",
                "url": "https://pokeapi.co/api/v2/pokemon-species/150/"
            }
        }
    ]
}

MEWTWO_SPECIES = {
    "id": 150,
    "name": "mewtwo",
    "gender_rate": -1,  # Genderless
    "capture_rate": 3,
    "base_happiness": 0,
    "hatch_counter": 30,
    "growth_rate": {
        "name": "slow",
        "url": "https://pokeapi.co/api/v2/growth-rate/1/"
    },
    "egg_groups": [
        {"name": "no-eggs", "url": "https://pokeapi.co/api/v2/egg-group/15/"}
    ],
    "names": [
        {
            "language": {"name": "ja-Hrkt", "url": "https://pokeapi.co/api/v2/language/1/"},
            "name": "ミュウツー"
        },
        {
            "language": {"name": "en", "url": "https://pokeapi.co/api/v2/language/9/"},
            "name": "Mewtwo"
        },
        {
            "language": {"name": "fr", "url": "https://pokeapi.co/api/v2/language/5/"},
            "name": "Mewtwo"
        }
    ],
    "genera": [
        {
            "genus": "Genetic Pokémon",
            "language": {"name": "en", "url": "https://pokeapi.co/api/v2/language/9/"}
        }
    ],
    "pokedex_numbers": [
        {
            "entry_number": 150,
            "pokedex": {"name": "kanto", "url": "https://pokeapi.co/api/v2/pokedex/2/"}
        }
    ],
    "evolution_chain": {
        "url": "https://pokeapi.co/api/v2/evolution-chain/83/"
    }
}

MEWTWO_POKEMON = {
    "id": 150,
    "name": "mewtwo",
    "height": 20,  # 2.0m
    "weight": 1220,  # 122.0kg
    "stats": [
        {"base_stat": 106, "stat": {"name": "hp"}, "effort": 0},
        {"base_stat": 110, "stat": {"name": "attack"}, "effort": 0},
        {"base_stat": 90, "stat": {"name": "defense"}, "effort": 0},
        {"base_stat": 154, "stat": {"name": "special-attack"}, "effort": 3},
        {"base_stat": 90, "stat": {"name": "special-defense"}, "effort": 0},
        {"base_stat": 130, "stat": {"name": "speed"}, "effort": 0}
    ],
    "types": [
        {"slot": 1, "type": {"name": "psychic", "url": "https://pokeapi.co/api/v2/type/14/"}}
    ],
    "sprites": {
        "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/150.png",
        "versions": {
            "generation-i": {
                "red-blue": {
                    "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-i/red-blue/150.png"
                }
            }
        }
    },
    "held_items": [
        {
            "item": {"name": "berserk-gene", "url": "https://pokeapi.co/api/v2/item/219/"},
            "version_details": [
                {"version": {"name": "gold", "url": "https://pokeapi.co/api/v2/version/4/"}, "rarity": 5}
            ]
        }
    ],
    "moves": [
        {
            "move": {"name": "confusion", "url": "https://pokeapi.co/api/v2/move/93/"},
            "version_group_details": [
                {
                    "level_learned_at": 1,
                    "move_learn_method": {"name": "level-up", "url": "https://pokeapi.co/api/v2/move-learn-method/1/"},
                    "version_group": {"name": "red-blue", "url": "https://pokeapi.co/api/v2/version-group/1/"}
                }
            ]
        },
        {
            "move": {"name": "psychic", "url": "https://pokeapi.co/api/v2/move/94/"},
            "version_group_details": [
                {
                    "level_learned_at": 75,
                    "move_learn_method": {"name": "level-up", "url": "https://pokeapi.co/api/v2/move-learn-method/1/"},
                    "version_group": {"name": "red-blue", "url": "https://pokeapi.co/api/v2/version-group/1/"}
                }
            ]
        },
        {
            "move": {"name": "thunder-wave", "url": "https://pokeapi.co/api/v2/move/86/"},
            "version_group_details": [
                {
                    "level_learned_at": 0,
                    "move_learn_method": {"name": "machine", "url": "https://pokeapi.co/api/v2/move-learn-method/4/"},
                    "version_group": {"name": "red-blue", "url": "https://pokeapi.co/api/v2/version-group/1/"}
                }
            ]
        }
    ]
}

PSYCHIC_TYPE_DATA = {
    "id": 14,
    "name": "psychic",
    "damage_relations": {
        "double_damage_from": [
            {"name": "bug", "url": "https://pokeapi.co/api/v2/type/7/"},
            {"name": "ghost", "url": "https://pokeapi.co/api/v2/type/8/"},
            {"name": "dark", "url": "https://pokeapi.co/api/v2/type/17/"}
        ],
        "half_damage_from": [
            {"name": "fighting", "url": "https://pokeapi.co/api/v2/type/2/"},
            {"name": "psychic", "url": "https://pokeapi.co/api/v2/type/14/"}
        ],
        "no_damage_from": []
    }
}

EVOLUTION_CHAIN_DATA = {
    "id": 83,
    "chain": {
        "species": {"name": "mewtwo", "url": "https://pokeapi.co/api/v2/pokemon-species/150/"},
        "evolves_to": []
    }
}

ENCOUNTERS_DATA = [
    {
        "location_area": {
            "name": "cerulean-cave-1f",
            "url": "https://pokeapi.co/api/v2/location-area/67/"
        },
        "version_details": [
            {
                "version": {"name": "red", "url": "https://pokeapi.co/api/v2/version/1/"},
                "encounter_details": [{"method": {"name": "walk"}}]
            },
            {
                "version": {"name": "blue", "url": "https://pokeapi.co/api/v2/version/2/"},
                "encounter_details": [{"method": {"name": "walk"}}]
            }
        ]
    }
]


def test_pokedex_detail_sync():
    """Test sync pokedex detail functionality."""
    client = Poke()
    
    try:
        with respx.mock(assert_all_called=False) as router:
            # Mock all required endpoints
            router.get("https://pokeapi.co/api/v2/pokedex/kanto").mock(
                return_value=Response(200, json=POKEDEX_DATA)
            )
            router.get("https://pokeapi.co/api/v2/pokemon-species/150").mock(
                return_value=Response(200, json=MEWTWO_SPECIES)
            )
            router.get("https://pokeapi.co/api/v2/pokemon-species/mewtwo").mock(
                return_value=Response(200, json=MEWTWO_SPECIES)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/150").mock(
                return_value=Response(200, json=MEWTWO_POKEMON)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/mewtwo").mock(
                return_value=Response(200, json=MEWTWO_POKEMON)
            )
            router.get("https://pokeapi.co/api/v2/type/psychic").mock(
                return_value=Response(200, json=PSYCHIC_TYPE_DATA)
            )
            router.get("https://pokeapi.co/api/v2/evolution-chain/83").mock(
                return_value=Response(200, json=EVOLUTION_CHAIN_DATA)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/150/encounters").mock(
                return_value=Response(200, json=ENCOUNTERS_DATA)
            )
            
            router.get("https://pokeapi.co/api/v2/pokemon/mewtwo/encounters").mock(
                return_value=Response(200, json=ENCOUNTERS_DATA)
            )
            
            # Test detail view
            detail = client.pokedex.detail(
                pokedex="kanto", 
                number=150, 
                version_group="red-blue"
            )
            
            # Basic info
            assert detail.name == "mewtwo"
            assert detail.national_no == 150
            assert detail.regional_no == 150
            assert detail.gender_ratio == "Genderless"
            assert detail.types == ["psychic"]
            assert detail.classification == "Genetic Pokémon"
            
            # Physical attributes
            assert detail.height_m == 2.0
            assert detail.weight_kg == 122.0
            assert detail.height_ft_in == "6'07\""
            assert abs(detail.weight_lbs - 269.0) < 0.1
            
            # Species info
            assert detail.capture_rate == 3
            assert detail.base_egg_steps == 7905  # 255 * (30 + 1)
            assert detail.growth_rate == "slow"
            assert detail.base_happiness == 0
            assert detail.egg_groups == ["no-eggs"]
            
            # EV yields
            assert len(detail.ev_yields) == 1
            assert detail.ev_yields[0].stat == "special-attack"
            assert detail.ev_yields[0].value == 3
            
            # Other names
            other_names = [n for n in detail.other_names if n.language == "ja-Hrkt"]
            assert len(other_names) == 1
            assert other_names[0].value == "ミュウツー"
            
            # Damage taken
            assert len(detail.damage_taken) > 0
            bug_damage = next((d for d in detail.damage_taken if d.type == "bug"), None)
            assert bug_damage is not None
            assert bug_damage.multiplier == 2.0
            
            # Wild held items
            assert "gold" in detail.wild_held_items
            assert "berserk-gene" in detail.wild_held_items["gold"]
            
            # Evolution chain
            assert detail.evolution_chain == ["mewtwo"]
            
            # Locations
            assert len(detail.locations) >= 2  # red and blue versions
            red_locations = [loc for loc in detail.locations if loc.version == "red"]
            assert len(red_locations) >= 1
            assert red_locations[0].location_area == "cerulean-cave-1f"
            
            # Moves
            assert len(detail.level_up_moves) >= 2
            level_1_moves = [m for m in detail.level_up_moves if m.level == 1]
            assert len(level_1_moves) >= 1
            assert level_1_moves[0].name == "confusion"
            
            assert len(detail.tm_hm_moves) >= 1
            tm_moves = [m for m in detail.tm_hm_moves if m.name == "thunder-wave"]
            assert len(tm_moves) >= 1
            
    finally:
        client._client = None


@pytest.mark.asyncio
async def test_pokedex_detail_async():
    """Test async pokedex detail functionality."""
    async with AsyncPoke() as client:
        with respx.mock(assert_all_called=False) as router:
            # Mock all required endpoints
            router.get("https://pokeapi.co/api/v2/pokedex/kanto").mock(
                return_value=Response(200, json=POKEDEX_DATA)
            )
            router.get("https://pokeapi.co/api/v2/pokemon-species/150").mock(
                return_value=Response(200, json=MEWTWO_SPECIES)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/150").mock(
                return_value=Response(200, json=MEWTWO_POKEMON)
            )
            router.get("https://pokeapi.co/api/v2/type/psychic").mock(
                return_value=Response(200, json=PSYCHIC_TYPE_DATA)
            )
            router.get("https://pokeapi.co/api/v2/evolution-chain/83").mock(
                return_value=Response(200, json=EVOLUTION_CHAIN_DATA)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/150/encounters").mock(
                return_value=Response(200, json=ENCOUNTERS_DATA)
            )
            router.get("https://pokeapi.co/api/v2/pokemon-species/mewtwo").mock(
                return_value=Response(200, json=MEWTWO_SPECIES)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/mewtwo").mock(
                return_value=Response(200, json=MEWTWO_POKEMON)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/mewtwo/encounters").mock(
                return_value=Response(200, json=ENCOUNTERS_DATA)
            )
            
            # Test detail view with concurrency
            detail = await client.pokedex.detail(
                pokedex="kanto",
                number=150,
                version_group="red-blue",
                concurrency=3
            )
            
            # Verify key data
            assert detail.name == "mewtwo"
            assert detail.national_no == 150
            assert detail.gender_ratio == "Genderless"
            assert detail.types == ["psychic"]
            assert detail.height_m == 2.0
            assert detail.weight_kg == 122.0
            
            # Verify damage calculations
            bug_damage = next((d for d in detail.damage_taken if d.type == "bug"), None)
            assert bug_damage.multiplier == 2.0
            
            fighting_damage = next((d for d in detail.damage_taken if d.type == "fighting"), None)
            assert fighting_damage.multiplier == 0.5


def test_gender_ratio_formatting():
    """Test gender ratio formatting edge cases."""
    from poke_api.resources.pokedex import format_gender_ratio
    
    # Genderless
    assert format_gender_ratio(-1) == "Genderless"
    
    # All female
    assert format_gender_ratio(8) == "M 0.0% / F 100.0%"
    
    # All male
    assert format_gender_ratio(0) == "M 100.0% / F 0.0%"
    
    # 50/50
    assert format_gender_ratio(4) == "M 50.0% / F 50.0%"
    
    # 87.5% male / 12.5% female (common for starters)
    assert format_gender_ratio(1) == "M 87.5% / F 12.5%"


def test_egg_steps_calculation():
    """Test egg steps calculation."""
    from poke_api.resources.pokedex import calc_egg_steps
    
    assert calc_egg_steps(20) == 5355  # 255 * (20 + 1)
    assert calc_egg_steps(30) == 7905  # 255 * (30 + 1)
    assert calc_egg_steps(0) == 255   # 255 * (0 + 1)


def test_height_weight_conversion():
    """Test height and weight conversions."""
    from poke_api.resources.pokedex import ft_in, kg_to_lbs
    
    # Height conversion (meters to feet/inches)
    assert ft_in(2.0) == "6'07\""
    assert ft_in(1.0) == "3'03\""
    assert ft_in(0.5) == "1'08\""
    
    # Weight conversion (kg to lbs)
    assert abs(kg_to_lbs(100.0) - 220.5) < 0.1
    assert abs(kg_to_lbs(50.0) - 110.2) < 0.1


def test_version_group_auto_selection():
    """Test automatic version group selection based on pokedex."""
    client = Poke()
    
    try:
        with respx.mock(assert_all_called=False) as router:
            router.get("https://pokeapi.co/api/v2/pokedex/kanto").mock(
                return_value=Response(200, json=POKEDEX_DATA)
            )
            router.get("https://pokeapi.co/api/v2/pokemon-species/150").mock(
                return_value=Response(200, json=MEWTWO_SPECIES)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/150").mock(
                return_value=Response(200, json=MEWTWO_POKEMON)
            )
            router.get("https://pokeapi.co/api/v2/type/psychic").mock(
                return_value=Response(200, json=PSYCHIC_TYPE_DATA)
            )
            router.get("https://pokeapi.co/api/v2/evolution-chain/83").mock(
                return_value=Response(200, json=EVOLUTION_CHAIN_DATA)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/150/encounters").mock(
                return_value=Response(200, json=ENCOUNTERS_DATA)
            )
            router.get("https://pokeapi.co/api/v2/pokemon-species/mewtwo").mock(
                return_value=Response(200, json=MEWTWO_SPECIES)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/mewtwo").mock(
                return_value=Response(200, json=MEWTWO_POKEMON)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/mewtwo/encounters").mock(
                return_value=Response(200, json=ENCOUNTERS_DATA)
            )
            
            # Test without explicit version_group - should auto-pick red-blue for kanto
            detail = client.pokedex.detail(pokedex="kanto", number=150)
            
            # Should have moves from red-blue version group
            level_up_moves = [m for m in detail.level_up_moves if m.version_group == "red-blue"]
            assert len(level_up_moves) >= 1
            
    finally:
        client._client = None


def test_resolve_number_by_name():
    """Test resolving Pokemon by name instead of number."""
    client = Poke()
    
    try:
        with respx.mock(assert_all_called=False) as router:
            router.get("https://pokeapi.co/api/v2/pokedex/kanto").mock(
                return_value=Response(200, json=POKEDEX_DATA)
            )
            router.get("https://pokeapi.co/api/v2/pokemon-species/mewtwo").mock(
                return_value=Response(200, json=MEWTWO_SPECIES)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/mewtwo").mock(
                return_value=Response(200, json=MEWTWO_POKEMON)
            )
            router.get("https://pokeapi.co/api/v2/type/psychic").mock(
                return_value=Response(200, json=PSYCHIC_TYPE_DATA)
            )
            router.get("https://pokeapi.co/api/v2/evolution-chain/83").mock(
                return_value=Response(200, json=EVOLUTION_CHAIN_DATA)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/mewtwo/encounters").mock(
                return_value=Response(200, json=ENCOUNTERS_DATA)
            )
            
            # Test with Pokemon name instead of number
            detail = client.pokedex.detail(
                pokedex="kanto",
                number="mewtwo",  # String name
                version_group="red-blue"
            )
            
            assert detail.name == "mewtwo"
            assert detail.national_no == 150
            
    finally:
        client._client = None