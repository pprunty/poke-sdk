"""Integration tests for client exception handling."""

import pytest
from unittest.mock import patch, MagicMock

from poke_api import Poke, AsyncPoke, NotFoundError, BadRequestError, ServerError


class TestClientExceptionHandling:
    """Test that clients properly map HTTP errors to exceptions."""

    def test_sync_client_404_error(self):
        """Test that sync client raises NotFoundError for 404."""
        client = Poke()
        
        # Mock httpx.request to return 404
        with patch('httpx.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = "Pokemon not found"
            mock_response.json.return_value = {"error": "Pokemon not found"}
            mock_request.return_value = mock_response
            
            with pytest.raises(NotFoundError) as exc_info:
                client.pokemon.get("nonexistent")
            
            assert exc_info.value.status_code == 404
            assert "Pokemon not found" in str(exc_info.value)

    def test_sync_client_400_error(self):
        """Test that sync client raises BadRequestError for 400."""
        client = Poke()
        
        with patch('httpx.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Invalid request"
            mock_response.json.return_value = {"error": "Invalid request format"}
            mock_request.return_value = mock_response
            
            with pytest.raises(BadRequestError) as exc_info:
                client.pokemon.get("invalid")
            
            assert exc_info.value.status_code == 400
            assert "Invalid request format" in str(exc_info.value)

    def test_sync_client_500_error(self):
        """Test that sync client raises ServerError for 500."""
        client = Poke()
        
        with patch('httpx.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_response.json.side_effect = Exception("Invalid JSON")
            mock_request.return_value = mock_response
            
            with pytest.raises(ServerError) as exc_info:
                client.pokemon.get("test")
            
            assert exc_info.value.status_code == 500
            assert "Internal server error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_async_client_404_error(self):
        """Test that async client raises NotFoundError for 404."""
        client = AsyncPoke()
        
        # Mock the async client's request method
        with patch.object(client._client, 'request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = "Pokemon not found"
            mock_response.json.return_value = {"error": "Pokemon not found"}
            mock_request.return_value = mock_response
            
            with pytest.raises(NotFoundError) as exc_info:
                await client.pokemon.get("nonexistent")
            
            assert exc_info.value.status_code == 404
            assert "Pokemon not found" in str(exc_info.value)
        
        await client.aclose()

    @pytest.mark.asyncio
    async def test_async_client_500_error(self):
        """Test that async client raises ServerError for 500."""
        client = AsyncPoke()
        
        with patch.object(client._client, 'request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_response.json.side_effect = Exception("Invalid JSON")
            mock_request.return_value = mock_response
            
            with pytest.raises(ServerError) as exc_info:
                await client.pokemon.get("test")
            
            assert exc_info.value.status_code == 500
            assert "Internal server error" in str(exc_info.value)
        
        await client.aclose()

    def test_real_404_still_works(self):
        """Test that real 404 requests still work with new exception handling."""
        client = Poke()
        
        with pytest.raises(NotFoundError) as exc_info:
            client.pokemon.get("definitely_nonexistent_pokemon_12345")
        
        assert exc_info.value.status_code == 404