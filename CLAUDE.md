# Purpose

This repository is a minimal, professional Python SDK for the public PokeAPI. It’s built for a take-home assignment and optimized for clarity, correctness, and developer experience—not bells and whistles. Keep it small, clean, and easy to review.

High-level goals (what “done” looks like)
Usable client(s)

Poke (sync) and AsyncPoke (async) with a configurable base_url property that defaults to https://pokeapi.co/api/v2.

One complete resource

pokemon resource with:

get(id_or_name) → returns a Pokémon (dict or typed model later).

list(limit=20, offset=0, type=None) → lists Pokémon; when type is provided, returns paginated set

Exceptions, not crashes

Thin exception hierarchy: PokeAPIError, APIConnectionError, APITimeoutError, APIStatusError, NotFoundError.

Pagination helper

A small iterator that follows next links until None.

Tests

Unit tests (mocked transport) and one integration test (hits real PokeAPI once) behind a marker.

Docs

README with quick start, examples, and how to run tests.

This file to guide code assistants (you, hi 👋) on intent & scope.

Polish but not over-engineered

Type markers (py.typed) already present.

Keep dependencies minimal (httpx + pydantic later).

Non-goals (for this assignment)
No full spec coverage beyond the pokemon resource.

No heavy caching layer or advanced rate-limit strategy.

No doc site generator, just README-level docs.

No complex CLI; a tiny demo entrypoint is okay if time allows.

Project Structure (reference)
bash
Copy
.
├── LICENSE
├── Makefile
├── README.md
├── SUBMISSION.md
├── poetry.lock
├── pyproject.toml
├── src
│   └── poke_api
│       ├── __init__.py
│       ├── _client.py
│       ├── _exceptions.py
│       ├── _utils
│       ├── _resources.py
│       ├── _types.py
│       ├── pagination.py
│       ├── py.typed
│       ├── resources
│       │   └── pokemon.py
│       └── types
└── tests
    ├── test_integraton.py
    └── test_pokemon_unit.py
Note: the test file name has a small typo (test_integraton.py). Prefer test_integration.py so it’s auto-discovered consistently.

What each piece is for
poke_api/_client.py – Core sync/async clients, base_url & timeout properties, _request method, resource injection.

poke_api/_exceptions.py – Minimal SDK exception types.

poke_api/resources/pokemon.py – PokemonResource & AsyncPokemonResource with get and list.

poke_api/pagination.py – Tiny iterator following next links (used by resources as needed).

poke_api/types/ – (Optional) typed models (e.g., Pydantic) if time permits.

tests/ – Unit tests (mock transport) + one integration test.

Implementation Notes (constraints for code assistants)
Keep it minimal. Favor tiny, readable functions over abstractions. No metaprogramming, no codegen.

HTTP: Use httpx. Sync uses httpx.request, async uses a single httpx.AsyncClient instance on the client.

Defaults:

base_url default: https://pokeapi.co/api/v2

timeout default: 10.0 seconds

Errors:

404 → NotFoundError

≥ 400 → APIStatusError(status_code, message?)

Network/timeout → APIConnectionError or APITimeoutError (you can map both to APIConnectionError to stay minimal)

Types:

Start with plain dicts for responses.

If time remains, add a minimal Pydantic model for Pokemon and swap it into pokemon.get.

Pagination:

Provide a helper iterate(url: str) that repeatedly GETs and yields each page’s results until next is None.

Testing:

Unit test: monkeypatch _request to return dummy responses.

Integration test (marked e.g. @pytest.mark.integration) to hit a real Pokémon (id=1).

Public API (target)
python
Copy
# Sync
from poke_api import Poke

client = Poke()  # uses default base_url
bulbasaur = client.pokemon.get(1)
page = client.pokemon.list(limit=10)

fire = client.pokemon.list(type="fire")  # names & URLs for fire-type Pokémon
python
Copy
# Async
from poke_api import AsyncPoke

client = AsyncPoke()

async def main() -> None:
    bulbasaur = await client.pokemon.get("bulbasaur")
    page = await client.pokemon.list(limit=10)
Exceptions:

python
Copy
from poke_api import NotFoundError, APIStatusError, APIConnectionError
Acceptance Criteria (checklist)
 Poke and AsyncPoke classes instantiate with no args and use the default base URL.

 client.pokemon.get(id_or_name) returns data for a valid Pokémon and raises NotFoundError on 404.

 client.pokemon.list(limit, offset) returns a page with count, results, and (optionally) respects type= when provided.

 pagination.iterate(url) yields successive result pages until next is None.

 Unit tests pass locally (pytest -q).

 Integration test passes (pytest -m integration).

 README quickstart code runs as-is.

 SUBMISSION.md explains design choices briefly.

Suggested tasks for a code assistant (Claude)
Clients & Exceptions

Implement Poke / AsyncPoke with base_url property and minimal _request that maps errors to exceptions.

Pokemon Resource

Implement get(id_or_name) and list(limit, offset, type=None) per above.

Pagination

Implement iterate(url) in pagination.py and use it where needed (optional for pokemon.list, but useful for future).

Tests

Add unit tests mocking _request to validate happy-path & error mapping.

Add a single integration test for pokemon.get(1) (Bulbasaur).

Docs & Hygiene

Ensure README usage examples reflect actual API.

Fix test_integraton.py → test_integration.py.

Keep dependencies minimal in pyproject.toml.

Trade-offs & future work
Validation: Start with dicts for speed; upgrade to Pydantic models if time remains.

Retries: Not required; can be added later with tenacity if flaky network becomes an issue.

More endpoints: Only pokemon is required; can add generation or type later behind the same pattern.

Caching: Out of scope; could add a small LRU or disk cache if needed.

Quick commands
bash
Copy
# Install
poetry install

# Lint / test
poetry run pytest -q
poetry run pytest -m integration

# Example (sync)
python -c "from poke_api import Poke; print(Poke().pokemon.get(1)['name'])"
If anything here conflicts with the assignment prompt, prefer the assignment requirements, keep code minimal, and document any trade-offs in SUBMISSION.md.