# tests/test_pokemon_unit.py

import httpx
from poke_api import Poke


class DummyResponse:
    def __init__(self, status_code, json_data):
        self.status_code, self._json = status_code, json_data

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("err", request=None, response=None)


def test_get_pokemon(monkeypatch):
    def fake_request(method, path, **kw):
        assert path == "/pokemon/1"
        return DummyResponse(
            200,
            {
                "id": 1,
                "name": "bulbasaur",
                "height": 7,
                "weight": 69,
                "base_experience": 64,
                "order": 1,
                "is_default": True,
                "location_area_encounters": (
                    "https://pokeapi.co/api/v2/pokemon/1/encounters"
                ),
                "species": {
                    "name": "bulbasaur",
                    "url": "https://pokeapi.co/api/v2/pokemon-species/1/",
                },
                "abilities": [],
                "types": [],
                "stats": [],
                "moves": [],
                "game_indices": [],
                "held_items": [],
                "forms": [],
                "past_abilities": [],
                "past_types": [],
            },
        )

    client = Poke()
    monkeypatch.setattr(Poke, "_request", lambda *a, **k: fake_request(*a[1:], **k))
    p = client.pokemon.get(1)  # Fixed: should be pokemon.get(), not pokemon_get()

    # Print API structure for debugging
    print(f"\n{'='*50}")
    print("API Response Structure:")
    from pprint import pprint

    pprint(p)
    print(f"{'='*50}")

    assert p.name == "bulbasaur"  # Now returns Pokemon model, not dict
