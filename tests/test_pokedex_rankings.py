"""Tests for Pokedex rankings functionality."""

import pytest
import respx
from httpx import Response

from poke_api import AsyncPoke, Poke

# Mock data
ORIGINAL_JOHTO_POKEDEX = {
    "id": 3,
    "name": "original-johto", 
    "pokemon_entries": [
        {
            "entry_number": 152,
            "pokemon_species": {
                "name": "chikorita",
                "url": "https://pokeapi.co/api/v2/pokemon-species/152/"
            }
        },
        {
            "entry_number": 155,
            "pokemon_species": {
                "name": "cyndaquil", 
                "url": "https://pokeapi.co/api/v2/pokemon-species/155/"
            }
        },
        {
            "entry_number": 158,
            "pokemon_species": {
                "name": "totodile",
                "url": "https://pokeapi.co/api/v2/pokemon-species/158/"
            }
        }
    ]
}

CHIKORITA_POKEMON = {
    "id": 152,
    "name": "chikorita",
    "height": 9,
    "weight": 64,
    "stats": [
        {"base_stat": 45, "stat": {"name": "hp"}},
        {"base_stat": 49, "stat": {"name": "attack"}},
        {"base_stat": 65, "stat": {"name": "defense"}},
        {"base_stat": 49, "stat": {"name": "special-attack"}},
        {"base_stat": 65, "stat": {"name": "special-defense"}},
        {"base_stat": 45, "stat": {"name": "speed"}}
    ],
    "types": [
        {"slot": 1, "type": {"name": "grass", "url": "https://pokeapi.co/api/v2/type/12/"}}
    ],
    "sprites": {
        "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/152.png",
        "versions": {
            "generation-ii": {
                "gold": {"front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-ii/gold/152.png"},
                "silver": {"front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-ii/silver/152.png"}
            }
        }
    }
}

CHIKORITA_SPECIES = {
    "id": 152,
    "name": "chikorita",
    "pokedex_numbers": [
        {
            "entry_number": 152,
            "pokedex": {"name": "original-johto", "url": "https://pokeapi.co/api/v2/pokedex/3/"}
        }
    ]
}

CYNDAQUIL_POKEMON = {
    "id": 155,
    "name": "cyndaquil", 
    "height": 5,
    "weight": 79,
    "stats": [
        {"base_stat": 39, "stat": {"name": "hp"}},
        {"base_stat": 52, "stat": {"name": "attack"}},
        {"base_stat": 43, "stat": {"name": "defense"}},
        {"base_stat": 60, "stat": {"name": "special-attack"}},
        {"base_stat": 50, "stat": {"name": "special-defense"}},
        {"base_stat": 65, "stat": {"name": "speed"}}
    ],
    "types": [
        {"slot": 1, "type": {"name": "fire", "url": "https://pokeapi.co/api/v2/type/10/"}}
    ],
    "sprites": {
        "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/155.png",
        "versions": {
            "generation-ii": {
                "gold": {"front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-ii/gold/155.png"},
                "silver": {"front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-ii/silver/155.png"}
            }
        }
    }
}

CYNDAQUIL_SPECIES = {
    "id": 155,
    "name": "cyndaquil",
    "pokedex_numbers": [
        {
            "entry_number": 155,
            "pokedex": {"name": "original-johto", "url": "https://pokeapi.co/api/v2/pokedex/3/"}
        }
    ]
}

TOTODILE_POKEMON = {
    "id": 158,
    "name": "totodile",
    "height": 6,
    "weight": 95,
    "stats": [
        {"base_stat": 50, "stat": {"name": "hp"}},
        {"base_stat": 65, "stat": {"name": "attack"}},
        {"base_stat": 64, "stat": {"name": "defense"}},
        {"base_stat": 44, "stat": {"name": "special-attack"}},
        {"base_stat": 48, "stat": {"name": "special-defense"}},
        {"base_stat": 43, "stat": {"name": "speed"}}
    ],
    "types": [
        {"slot": 1, "type": {"name": "water", "url": "https://pokeapi.co/api/v2/type/11/"}}
    ],
    "sprites": {
        "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/158.png",
        "versions": {
            "generation-ii": {
                "gold": {"front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-ii/gold/158.png"},
                "silver": {"front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-ii/silver/158.png"}
            }
        }
    }
}

TOTODILE_SPECIES = {
    "id": 158,
    "name": "totodile",
    "pokedex_numbers": [
        {
            "entry_number": 158,
            "pokedex": {"name": "original-johto", "url": "https://pokeapi.co/api/v2/pokedex/3/"}
        }
    ]
}


def test_pokedex_rankings_sync():
    """Test sync pokedex rankings functionality."""
    client = Poke()
    
    try:
        with respx.mock() as router:
            # Mock pokedex endpoint
            router.get("https://pokeapi.co/api/v2/pokedex/original-johto").mock(
                return_value=Response(200, json=ORIGINAL_JOHTO_POKEDEX)
            )
            
            # Mock pokemon endpoints
            router.get("https://pokeapi.co/api/v2/pokemon/chikorita").mock(
                return_value=Response(200, json=CHIKORITA_POKEMON)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/cyndaquil").mock(
                return_value=Response(200, json=CYNDAQUIL_POKEMON)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/totodile").mock(
                return_value=Response(200, json=TOTODILE_POKEMON)
            )
            
            # Mock species endpoints  
            router.get("https://pokeapi.co/api/v2/pokemon-species/chikorita").mock(
                return_value=Response(200, json=CHIKORITA_SPECIES)
            )
            router.get("https://pokeapi.co/api/v2/pokemon-species/cyndaquil").mock(
                return_value=Response(200, json=CYNDAQUIL_SPECIES)
            )
            router.get("https://pokeapi.co/api/v2/pokemon-species/totodile").mock(
                return_value=Response(200, json=TOTODILE_SPECIES)
            )
            
            # Test rankings
            rows = client.pokedex.rankings(pokedex="original-johto")
            
            # Should have 3 rows
            assert len(rows) == 3
            
            # Check sorting by total base stat (totodile=314, cyndaquil=309, chikorita=318)
            # So chikorita should be rank 1, totodile rank 2, cyndaquil rank 3
            assert rows[0].name == "chikorita"
            assert rows[0].rank == 1
            assert rows[0].total_base_stat == 318
            assert rows[0].regional_no == 152
            assert rows[0].national_no == 152
            assert rows[0].types == ["grass"]
            assert rows[0].sprite_url is not None
            
            assert rows[1].name == "totodile"
            assert rows[1].rank == 2
            assert rows[1].total_base_stat == 314
            
            assert rows[2].name == "cyndaquil" 
            assert rows[2].rank == 3
            assert rows[2].total_base_stat == 309
            
    finally:
        client._client = None


@pytest.mark.asyncio
async def test_pokedex_rankings_async():
    """Test async pokedex rankings functionality."""
    async with AsyncPoke() as client:
        with respx.mock() as router:
            # Mock pokedex endpoint
            router.get("https://pokeapi.co/api/v2/pokedex/original-johto").mock(
                return_value=Response(200, json=ORIGINAL_JOHTO_POKEDEX)
            )
            
            # Mock pokemon endpoints
            router.get("https://pokeapi.co/api/v2/pokemon/chikorita").mock(
                return_value=Response(200, json=CHIKORITA_POKEMON)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/cyndaquil").mock(
                return_value=Response(200, json=CYNDAQUIL_POKEMON)
            )
            router.get("https://pokeapi.co/api/v2/pokemon/totodile").mock(
                return_value=Response(200, json=TOTODILE_POKEMON)
            )
            
            # Mock species endpoints
            router.get("https://pokeapi.co/api/v2/pokemon-species/chikorita").mock(
                return_value=Response(200, json=CHIKORITA_SPECIES)
            )
            router.get("https://pokeapi.co/api/v2/pokemon-species/cyndaquil").mock(
                return_value=Response(200, json=CYNDAQUIL_SPECIES)
            )
            router.get("https://pokeapi.co/api/v2/pokemon-species/totodile").mock(
                return_value=Response(200, json=TOTODILE_SPECIES)
            )
            
            # Test rankings with concurrency
            rows = await client.pokedex.rankings(pokedex="original-johto", concurrency=3)
            
            # Should have 3 rows sorted by total base stat
            assert len(rows) == 3
            
            # Verify sorting and basic data
            assert rows[0].name == "chikorita"
            assert rows[0].rank == 1
            assert rows[0].total_base_stat == 318
            
            assert rows[1].name == "totodile"
            assert rows[1].rank == 2
            assert rows[1].total_base_stat == 314
            
            assert rows[2].name == "cyndaquil"
            assert rows[2].rank == 3
            assert rows[2].total_base_stat == 309


def test_sprite_preference_sync():
    """Test sprite preference selection in rankings."""
    client = Poke()
    
    try:
        with respx.mock() as router:
            # Mock endpoints with minimal data for sprite testing
            router.get("https://pokeapi.co/api/v2/pokedex/original-johto").mock(
                return_value=Response(200, json={
                    "pokemon_entries": [{
                        "entry_number": 152,
                        "pokemon_species": {"name": "chikorita"}
                    }]
                })
            )
            
            router.get("https://pokeapi.co/api/v2/pokemon/chikorita").mock(
                return_value=Response(200, json=CHIKORITA_POKEMON)
            )
            
            router.get("https://pokeapi.co/api/v2/pokemon-species/chikorita").mock(
                return_value=Response(200, json=CHIKORITA_SPECIES)
            )
            
            # Test with explicit sprite preference
            rows = client.pokedex.rankings(pokedex="original-johto", sprite_preference="gold")
            
            assert len(rows) == 1
            # Should pick gold sprite over default
            assert "gold" in rows[0].sprite_url
            
    finally:
        client._client = None


def test_empty_pokedex():
    """Test handling of empty pokedex.""" 
    client = Poke()
    
    try:
        with respx.mock() as router:
            router.get("https://pokeapi.co/api/v2/pokedex/empty").mock(
                return_value=Response(200, json={"pokemon_entries": []})
            )
            
            rows = client.pokedex.rankings(pokedex="empty")
            assert rows == []
            
    finally:
        client._client = None