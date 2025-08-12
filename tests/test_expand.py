import pytest
import respx
from httpx import Response
from poke_api import AsyncPoke, Poke

# Mock data for testing
BULBA = {
    "id": 1,
    "name": "bulbasaur",
    "moves": [
        {
            "move": {"name": "tackle", "url": "https://pokeapi.co/api/v2/move/1/"},
            "version_group_details": [],
        }
    ],
    "species": {
        "name": "bulbasaur",
        "url": "https://pokeapi.co/api/v2/pokemon-species/1/",
    },
    "types": [
        {
            "slot": 1,
            "type": {"name": "grass", "url": "https://pokeapi.co/api/v2/type/12/"},
        }
    ],
}

MOVE_1 = {
    "id": 1,
    "name": "pound",
    "type": {"name": "normal", "url": "https://pokeapi.co/api/v2/type/1/"},
}

SPECIES_1 = {
    "id": 1,
    "name": "bulbasaur",
    "generation": {
        "name": "generation-i",
        "url": "https://pokeapi.co/api/v2/generation/1/",
    },
}

TYPE_12 = {"id": 12, "name": "grass"}

TYPE_1 = {"id": 1, "name": "normal"}


@pytest.mark.asyncio
async def test_expand_async_moves():
    """Test async expansion with path filtering on moves."""
    async with AsyncPoke() as client:
        with respx.mock(assert_all_called=True) as router:
            router.get("https://pokeapi.co/api/v2/move/1/").mock(
                return_value=Response(200, json=MOVE_1)
            )
            expanded = await client.expand(
                BULBA, paths=["moves.move"], depth=1, max_requests=10, concurrency=3
            )

        # Check that the move was expanded
        ref = expanded["moves"][0]["move"]
        assert ref["name"] == "tackle"
        assert "__expanded__" in ref
        assert ref["__expanded__"]["id"] == 1
        assert ref["__expanded__"]["name"] == "pound"


def test_expand_sync_moves():
    """Test sync expansion with path filtering on moves."""
    client = Poke()
    try:
        with respx.mock(assert_all_called=True) as router:
            router.get("https://pokeapi.co/api/v2/move/1/").mock(
                return_value=Response(200, json=MOVE_1)
            )
            expanded = client.expand(
                BULBA, paths=["moves.move"], depth=1, max_requests=10
            )

        # Check that the move was expanded
        ref = expanded["moves"][0]["move"]
        assert ref["name"] == "tackle"
        assert "__expanded__" in ref
        assert ref["__expanded__"]["id"] == 1
        assert ref["__expanded__"]["name"] == "pound"
    finally:
        client._client = None  # Clean up since Poke doesn't have close method


@pytest.mark.asyncio
async def test_expand_async_no_paths():
    """Test async expansion without path filtering (expand immediate refs only)."""
    async with AsyncPoke() as client:
        with respx.mock() as router:
            router.get("https://pokeapi.co/api/v2/pokemon-species/1/").mock(
                return_value=Response(200, json=SPECIES_1)
            )

            expanded = await client.expand(BULBA, depth=1, max_requests=10)

        # Check that only immediate refs were expanded (species), not nested ones (moves, types)
        move_ref = expanded["moves"][0]["move"]
        species_ref = expanded["species"]
        type_ref = expanded["types"][0]["type"]

        assert "__expanded__" not in move_ref  # Not immediate, so not expanded
        assert "__expanded__" in species_ref  # Immediate, so expanded
        assert "__expanded__" not in type_ref  # Not immediate, so not expanded

        assert species_ref["__expanded__"]["name"] == "bulbasaur"


@pytest.mark.asyncio
async def test_expand_async_depth_limit():
    """Test depth limiting in async expansion."""
    async with AsyncPoke() as client:
        with respx.mock() as router:
            router.get("https://pokeapi.co/api/v2/move/1/").mock(
                return_value=Response(200, json=MOVE_1)
            )
            router.get("https://pokeapi.co/api/v2/type/1/").mock(
                return_value=Response(200, json=TYPE_1)
            )

            # Depth=2 should expand move -> type
            expanded = await client.expand(
                BULBA, paths=["moves.move"], depth=2, max_requests=10
            )

        # Check depth-2 expansion
        move_ref = expanded["moves"][0]["move"]
        assert "__expanded__" in move_ref

        # The type inside the expanded move should also be expanded
        type_ref = move_ref["__expanded__"]["type"]
        assert "__expanded__" in type_ref
        assert type_ref["__expanded__"]["name"] == "normal"


def test_expand_sync_max_requests():
    """Test max_requests budget limiting in sync expansion."""
    client = Poke()
    try:
        with respx.mock() as router:
            # Only one request should be made due to max_requests=1
            router.get("https://pokeapi.co/api/v2/move/1/").mock(
                return_value=Response(200, json=MOVE_1)
            )

            expanded = client.expand(
                BULBA, paths=["moves.move"], depth=1, max_requests=1
            )

        # Only the move should be expanded, not the species or type
        move_ref = expanded["moves"][0]["move"]
        species_ref = expanded["species"]
        type_ref = expanded["types"][0]["type"]

        assert "__expanded__" in move_ref
        assert "__expanded__" not in species_ref
        assert "__expanded__" not in type_ref
    finally:
        client._client = None


@pytest.mark.asyncio
async def test_expand_async_concurrency():
    """Test that async expansion respects concurrency limits."""
    async with AsyncPoke() as client:
        with respx.mock() as router:
            router.get("https://pokeapi.co/api/v2/move/1/").mock(
                return_value=Response(200, json=MOVE_1)
            )

            # Test with low concurrency using paths to target specific refs
            expanded = await client.expand(
                BULBA,
                paths=["moves.move"],  # Specify path to ensure expansion
                depth=1,
                max_requests=10,
                concurrency=1,
            )

        # Should still work, just slower
        move_ref = expanded["moves"][0]["move"]
        species_ref = expanded["species"]
        type_ref = expanded["types"][0]["type"]

        assert "__expanded__" in move_ref
        assert "__expanded__" not in species_ref  # Not in specified paths
        assert "__expanded__" not in type_ref  # Not in specified paths


def test_expand_sync_deduplication():
    """Test that URLs are not fetched twice."""
    # Create data with duplicate URL references
    data_with_duplicates = {
        "moves": [
            {"move": {"name": "tackle", "url": "https://pokeapi.co/api/v2/move/1/"}},
            {
                "move": {"name": "tackle", "url": "https://pokeapi.co/api/v2/move/1/"}
            },  # Same URL
        ]
    }

    client = Poke()
    try:
        with respx.mock() as router:
            # This should be called only once due to deduplication
            route = router.get("https://pokeapi.co/api/v2/move/1/").mock(
                return_value=Response(200, json=MOVE_1)
            )

            expanded = client.expand(
                data_with_duplicates,
                paths=["moves.move"],  # Specify path to target move references
                depth=1,
                max_requests=10,
            )

            # Verify both moves are expanded but URL was only fetched once
            assert "__expanded__" in expanded["moves"][0]["move"]
            assert "__expanded__" in expanded["moves"][1]["move"]
            assert route.call_count == 1
    finally:
        client._client = None


@pytest.mark.asyncio
async def test_expand_async_empty_data():
    """Test expansion on empty or non-expandable data."""
    async with AsyncPoke() as client:
        # Test with empty dict
        result = await client.expand({}, depth=1, max_requests=10)
        assert result == {}

        # Test with data containing no refs
        no_refs = {"id": 1, "name": "test", "value": 42}
        result = await client.expand(no_refs, depth=1, max_requests=10)
        assert result == no_refs


def test_expand_preserves_original():
    """Test that expansion doesn't mutate the original data."""
    original = {"move": {"name": "tackle", "url": "https://pokeapi.co/api/v2/move/1/"}}
    original_copy = original.copy()

    client = Poke()
    try:
        with respx.mock() as router:
            router.get("https://pokeapi.co/api/v2/move/1/").mock(
                return_value=Response(200, json=MOVE_1)
            )

            expanded = client.expand(original, depth=1, max_requests=10)

            # Original should be unchanged
            assert original == original_copy
            assert "__expanded__" not in original["move"]

            # But expanded should have the expansion
            assert "__expanded__" in expanded["move"]
    finally:
        client._client = None
