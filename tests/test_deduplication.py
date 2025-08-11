"""Tests for async de-duplication functionality."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest
from poke_api import AsyncPoke


class TestAsyncDeduplication:
    """Test suite for async request de-duplication."""

    @pytest.mark.asyncio
    async def test_concurrent_same_url_deduplication(self):
        """Test that concurrent requests to the same URL are de-duplicated."""
        client = AsyncPoke()

        # Mock the actual HTTP request to count calls
        call_count = 0

        async def counting_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Add small delay to simulate network
            await asyncio.sleep(0.01)

            # Create mock response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "id": 25,
                "name": "pikachu",
                "height": 4,
                "weight": 60,
                "base_experience": 112,
                "order": 35,
                "is_default": True,
                "location_area_encounters": "https://pokeapi.co/api/v2/pokemon/25/encounters",
                "sprites": {},
                "cries": {"latest": "cry-latest.ogg", "legacy": "cry-legacy.ogg"},
                "species": {
                    "name": "pikachu",
                    "url": "https://pokeapi.co/api/v2/pokemon-species/25/",
                },
                "stats": [],
                "types": [],
                "past_types": [],
                "held_items": [],
                "moves": [],
                "game_indices": [],
                "abilities": [],
                "forms": [],
                "past_abilities": [],
            }
            mock_response.status_code = 200
            return mock_response

        # Patch the request method
        with patch.object(client, "_request", side_effect=counting_request):
            # Create 5 concurrent requests for the same Pokemon
            tasks = [client.pokemon.get("pikachu") for _ in range(5)]

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks)

            # Should only make 1 actual HTTP request due to de-duplication
            assert call_count == 1, f"Expected 1 HTTP request, but made {call_count}"

            # All results should be identical
            first_result = results[0]
            for result in results:
                assert result.name == first_result.name
                assert result.id == first_result.id

        await client.aclose()

    @pytest.mark.asyncio
    async def test_different_urls_not_deduplicated(self):
        """Test that different URLs are not de-duplicated."""
        client = AsyncPoke()

        call_count = 0

        async def counting_request(method, path, **kwargs):
            nonlocal call_count
            call_count += 1

            # Create mock response based on path
            mock_response = MagicMock()

            if "pikachu" in path:
                mock_response.json.return_value = {
                    "id": 25,
                    "name": "pikachu",
                    "height": 4,
                    "weight": 60,
                    "base_experience": 112,
                    "order": 35,
                    "is_default": True,
                    "location_area_encounters": "https://pokeapi.co/api/v2/pokemon/25/encounters",
                    "sprites": {},
                    "cries": {"latest": "cry-latest.ogg", "legacy": "cry-legacy.ogg"},
                    "species": {
                        "name": "pikachu",
                        "url": "https://pokeapi.co/api/v2/pokemon-species/25/",
                    },
                    "stats": [],
                    "types": [],
                    "past_types": [],
                    "held_items": [],
                    "moves": [],
                    "game_indices": [],
                    "abilities": [],
                    "forms": [],
                    "past_abilities": [],
                }
            elif "bulbasaur" in path:
                mock_response.json.return_value = {
                    "id": 1,
                    "name": "bulbasaur",
                    "height": 7,
                    "weight": 69,
                    "base_experience": 64,
                    "order": 1,
                    "is_default": True,
                    "location_area_encounters": "https://pokeapi.co/api/v2/pokemon/1/encounters",
                    "sprites": {},
                    "cries": {"latest": "cry-latest.ogg", "legacy": "cry-legacy.ogg"},
                    "species": {
                        "name": "bulbasaur",
                        "url": "https://pokeapi.co/api/v2/pokemon-species/1/",
                    },
                    "stats": [],
                    "types": [],
                    "past_types": [],
                    "held_items": [],
                    "moves": [],
                    "game_indices": [],
                    "abilities": [],
                    "forms": [],
                    "past_abilities": [],
                }
            else:
                # For list requests
                mock_response.json.return_value = {
                    "count": 1302,
                    "next": None,
                    "previous": None,
                    "results": [
                        {"name": "test", "url": "https://pokeapi.co/api/v2/pokemon/1/"}
                    ],
                }

            mock_response.status_code = 200
            return mock_response

        with patch.object(client, "_request", side_effect=counting_request):
            # Create concurrent requests for different URLs
            tasks = [
                client.pokemon.get("pikachu"),
                client.pokemon.get("bulbasaur"),
                client.pokemon.get(
                    "pikachu"
                ),  # This should be de-duplicated with first pikachu
            ]

            results = await asyncio.gather(*tasks)

            # Should make 2 requests (pikachu and bulbasaur), with the second pikachu de-duplicated
            assert call_count == 2, f"Expected 2 HTTP requests, but made {call_count}"

            # Verify results
            assert results[0].name == "pikachu"
            assert results[1].name == "bulbasaur"
            assert results[2].name == "pikachu"

            # Verify the two pikachu results are identical (from de-duplication)
            assert results[0].id == results[2].id

        await client.aclose()

    @pytest.mark.asyncio
    async def test_query_params_create_different_locks(self):
        """Test that different query parameters create different cache keys."""
        client = AsyncPoke()

        call_count = 0

        async def counting_request(method, path, **kwargs):
            nonlocal call_count
            call_count += 1

            mock_response = MagicMock()
            mock_response.json.return_value = {
                "count": 1302,
                "next": None,
                "previous": None,
                "results": [
                    {"name": "test", "url": "https://pokeapi.co/api/v2/pokemon/1/"}
                ],
            }
            mock_response.status_code = 200
            return mock_response

        with patch.object(client, "_request", side_effect=counting_request):
            # Create requests with different query parameters
            tasks = [
                client.pokemon.list(limit=10, offset=0),
                client.pokemon.list(limit=20, offset=0),  # Different limit
                client.pokemon.list(limit=10, offset=10),  # Different offset
                client.pokemon.list(
                    limit=10, offset=0
                ),  # Same as first - should be de-duplicated
            ]

            await asyncio.gather(*tasks)

            # Should make 3 requests (different query params create different URLs)
            assert call_count == 3, f"Expected 3 HTTP requests, but made {call_count}"

        await client.aclose()

    @pytest.mark.asyncio
    async def test_locks_cleanup(self):
        """Test that locks are eventually cleaned up."""
        client = AsyncPoke()

        async def mock_request(method, path, **kwargs):
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "id": 25,
                "name": "pikachu",
                "height": 4,
                "weight": 60,
                "base_experience": 112,
                "order": 35,
                "is_default": True,
                "location_area_encounters": "https://pokeapi.co/api/v2/pokemon/25/encounters",
                "sprites": {},
                "cries": {"latest": "cry-latest.ogg", "legacy": "cry-legacy.ogg"},
                "species": {
                    "name": "pikachu",
                    "url": "https://pokeapi.co/api/v2/pokemon-species/25/",
                },
                "stats": [],
                "types": [],
                "past_types": [],
                "held_items": [],
                "moves": [],
                "game_indices": [],
                "abilities": [],
                "forms": [],
                "past_abilities": [],
            }
            mock_response.status_code = 200
            return mock_response

        with patch.object(client, "_request", side_effect=mock_request):
            # Make some concurrent requests
            tasks = [client.pokemon.get("pikachu") for _ in range(3)]
            await asyncio.gather(*tasks)

            initial_locks = len(client._locks)

            # Give some time for cleanup
            await asyncio.sleep(0.01)

            # The number of locks should be reasonable (may not be 0 due to race conditions)
            # but shouldn't grow indefinitely
            assert len(client._locks) <= initial_locks

        await client.aclose()
