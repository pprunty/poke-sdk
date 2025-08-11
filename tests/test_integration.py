"""Integration tests that hit the real PokeAPI."""

import pytest
from poke_api import AsyncPoke, Poke
from poke_api._exceptions import NotFoundError
from poke_api.types.pokemon import Pokemon


@pytest.mark.integration
class TestPokemonIntegration:
    """Integration tests for pokemon resource."""

    def test_get_bulbasaur_real_api(self):
        """Test getting Bulbasaur (ID=1) from real PokeAPI."""
        client = Poke()

        # Get Bulbasaur by ID
        result = client.pokemon.get(1)

        # Verify basic structure and content
        assert isinstance(result, Pokemon)
        assert result.id == 1
        assert result.name == "bulbasaur"
        assert result.height > 0
        assert result.weight > 0
        assert len(result.types) > 0

    def test_get_bulbasaur_by_name_real_api(self):
        """Test getting Bulbasaur by name from real PokeAPI."""
        client = Poke()

        # Get Bulbasaur by name
        result = client.pokemon.get("bulbasaur")

        # Verify basic structure and content
        assert isinstance(result, Pokemon)
        assert result.id == 1
        assert result.name == "bulbasaur"

    def test_list_pokemon_real_api(self):
        """Test listing pokemon from real PokeAPI."""
        client = Poke()

        # Get first 5 pokemon
        result = client.pokemon.list(limit=5, offset=0)

        # Verify structure - now returns Page[NamedAPIResource]
        from poke_api.pagination import Page

        assert isinstance(result, Page)
        assert result.count > 1000  # There are many pokemon
        assert len(result.result) == 5

        # Verify first pokemon is Bulbasaur
        first_pokemon = result.result[0]
        assert first_pokemon.name == "bulbasaur"
        assert hasattr(first_pokemon, "url")

    def test_get_nonexistent_pokemon_real_api(self):
        """Test that getting a nonexistent pokemon raises NotFoundError."""
        client = Poke()

        with pytest.raises(NotFoundError):
            client.pokemon.get("definitely-not-a-pokemon-12345")

    @pytest.mark.asyncio
    async def test_async_get_bulbasaur_real_api(self):
        """Test getting Bulbasaur with async client from real PokeAPI."""
        client = AsyncPoke()

        try:
            # Get Bulbasaur by ID
            result = await client.pokemon.get(1)

            # Verify basic structure and content
            assert isinstance(result, Pokemon)
            assert result.id == 1
            assert result.name == "bulbasaur"
            assert result.height > 0
            assert result.weight > 0
        finally:
            await client.aclose()

    @pytest.mark.asyncio
    async def test_async_list_pokemon_real_api(self):
        """Test async pokemon listing from real PokeAPI."""
        client = AsyncPoke()

        try:
            # Get first 3 pokemon
            result = await client.pokemon.list(limit=3, offset=0)

            # Verify structure - now returns AsyncPage[NamedAPIResource]
            from poke_api.pagination import AsyncPage

            assert isinstance(result, AsyncPage)
            assert result.count > 1000
            assert len(result.result) == 3
        finally:
            await client.aclose()

    def test_list_pokemon_by_type_real_api(self):
        """Test listing pokemon from real PokeAPI with basic pagination."""
        client = Poke()

        # Get first 5 pokemon (type filtering not implemented yet)
        result = client.pokemon.list(limit=5)

        # Verify structure - now returns Page[NamedAPIResource]
        from poke_api.pagination import Page

        assert isinstance(result, Page)
        assert result.count > 1000  # There are many pokemon
        assert len(result.result) <= 5

        # Verify each result has name and url
        for pokemon in result.result:
            assert pokemon.name  # Non-empty name
            assert pokemon.url  # Has URL
