# PokeAPI Python API Library

![header](./header.png)

The PokeAPI Python Library provides access to [PokeAPI](https://pokeapi.co/) APIs from Python 3.8 applications (haven't tested on other versions). The library includes type definitions for all APIs, including request params and response fields, and offers both synchronous and asynchronous clients powered by httpx.

Thanks to [PokeAPI](https://pokeapi.co/) for maintaining and making the APIs publicly accessible.

## Documentation

The REST API documentation can be found at <pokeapi.co/docs>. The live site crashes... always. But the APIs are pretty reliable.

## Requirements

* python 3.8+

## Installation

### pip

```
pip install poke_sdk
```

> [!NOTE]
> I haven't pushed this to pip (yet). Follow instructions below for manual installation

### Development

```bash
git clone https://github.com/pprunty/poke-sdk.git && cd poke-sdk
```

```bash
make install
```

**Run examples**:

```
make example <example_file_name> 
```

## Usage

```python
from poke_api import Poke

client = Poke()

# Get a Pokemon by ID or name
pikachu = client.pokemon.get(id=25)
print(pikachu)
# Output: Pokemon(id=25, name='pikachu', lists={abilities: 2, forms: 1, moves: 105, types: 1})

# List Pokemon with pagination - returns Page[NamedAPIResource]
pokemon_page = client.pokemon.list(limit=5)
print(pokemon_page)
# Output: Page(items=5, count=1302, has_next=True)
```

## Async Usage

```python
from poke_api import AsyncPoke

client = AsyncPoke()

async def main() -> None:
    pikachu = await client.pokemon.get(name="pikachu")
    print(pikachu)
```

## Object Representation

Objects print a concise summary by default, showing key fields and list counts. For full data access, use `.to_dict()` or `.to_json()`:

```python
# Friendly printing (default behavior)
pikachu = client.pokemon.get("pikachu")
print(pikachu)
# Output: Pokemon(id=25, name='pikachu', lists={abilities: 2, moves: 105, types: 1})

# Multi-line summary
print(pikachu.summary())
# Output:
# Pokemon:
#   id: 25
#   name: pikachu
#   height: 4
#   weight: 60
#   abilities: 2 items
#   moves: 105 items

# Full data access
pokemon_dict = pikachu.to_dict()    # Returns dictionary with all fields
pokemon_json = pikachu.to_json()    # Returns JSON string with all data
```

## Types

All models inherit from `BaseModel` and provide:
* `.to_dict()` - Convert to dictionary representation
* `.to_json()` - Convert to JSON string representation
* `.summary()` - Multi-line pretty summary

## Search


## Pokédex

[serebii.net](https://serebii.net/pokedex)

> [!WARNING]
> The 

## Project Structure

```bash
.
├── src/poke_api/               # Main SDK package
│   ├── _client.py              # Sync/async HTTP clients with retry logic
│   ├── _exceptions.py          # SDK exception hierarchy
│   ├── _resource.py            # Base resource classes with caching
│   ├── _types.py               # Common types and BaseModel with friendly printing
│   ├── pagination.py           # Page/AsyncPage classes with auto-iteration
│   ├── resources/              # API resource implementations (pokemon, generation)
│   └── types/                  # Pydantic models for API responses
├── tests/                      # Unit and integration tests
├── examples/                   # Usage examples organized by resource type
├── pyproject.toml              # Poetry config and dependencies
└── README.md                   # Documentation
```

## Pagination

List methods in the PokeAPI are paginated.

This library provides auto-paginating iterators with each list response, so you do not have to request successive pages manually:

```python
from poke_api import Poke

client = Poke()

all_pokemon = []
# Automatically fetches more pages as needed.
# Note: This will fetch ALL Pokemon (1300+) - use limit for demos
for pokemon in client.pokemon.list(limit=50):  # Limit for demo
    # Do something with pokemon here
    all_pokemon.append(pokemon)
print(all_pokemon)
```

Or, asynchronously:

```python
import asyncio
from poke_api import AsyncPoke

client = AsyncPoke()

async def main() -> None:
    all_pokemon = []
    # Iterate through items across all pages, issuing requests as needed.
    # Note: This will fetch ALL Pokemon (1300+) - use limit for demos
    async for pokemon in client.pokemon.list(limit=50):  # Limit for demo
        all_pokemon.append(pokemon)
    print(all_pokemon)

asyncio.run(main())
```

Alternatively, you can use the `.has_next_page()`, `.next_page_info()`, or `.get_next_page()` methods for more granular control working with pages:

```python
first_page = client.pokemon.list()
if first_page.has_next_page():
    print(f"will fetch next page using these details: {first_page.next_page_info()}")
    next_page = first_page.get_next_page()
    print(f"number of items we just fetched: {len(next_page.result)}")

# Add `await` for async usage.
```

Or just work directly with the returned data:

```python
first_page = client.pokemon.list()
for pokemon in first_page.result:
    print(pokemon.name)

# Add `await` for async usage.
```

## Caching

The SDK includes built-in intelligent caching using [cachetools](https://github.com/tkem/cachetools/) to improve performance and reduce API calls.

### Cache Type and Configuration

- **Cache Type**: TTL (Time-To-Live) cache with automatic expiration
- **Default Settings**: 1024 items max, 60-second TTL per item
- **Scope**: Per-resource caching (each resource has its own cache)
- **Behavior**: Identical requests within TTL window return cached results

```python
from poke_api import Poke

client = Poke()

# First call hits the API
pikachu1 = client.pokemon.get("pikachu")  # ~200ms API call

# Second call uses cached data (within 60 seconds)
pikachu2 = client.pokemon.get("pikachu")  # ~1ms cache hit
```

### Sync vs Async Caching

**Sync Caching (Poke)**:
- Uses `@cachedmethod` decorator for automatic caching
- Thread-safe operations
- Immediate cache hits

**Async Caching (AsyncPoke)**:
- Manual cache management with async locks
- Request de-duplication: concurrent requests for same URL share results
- Automatic lock cleanup to prevent memory leaks

```python
# Async example - concurrent requests are de-duplicated
import asyncio
from poke_api import AsyncPoke

client = AsyncPoke()

async def get_pokemon():
    # These 3 concurrent requests will result in only 1 API call
    tasks = [
        client.pokemon.get("pikachu"),
        client.pokemon.get("pikachu"),
        client.pokemon.get("pikachu")
    ]
    results = await asyncio.gather(*tasks)
    return results

# All 3 results are identical, but only 1 API call was made
```

### Cache Customization

Currently, cache settings are fixed per resource. For advanced use cases, you can access the underlying cache:

```python
# Access cache directly (advanced usage)
cache = client.pokemon._cache
print(f"Cache size: {len(cache)} items")
print(f"Cache info: {cache.currsize}/{cache.maxsize} items")

# Clear cache if needed
cache.clear()
```

### Performance Benefits

Caching provides significant speedups for repeated operations:

- **Individual lookups**: 100-200x faster for cache hits
- **Search operations**: Benefits from cached intermediate data
- **Pagination**: Cached page data improves navigation performance

For more advanced caching configurations, see the [cachetools documentation](https://cachetools.readthedocs.io/).

## Retries and Timeouts

The SDK includes built-in retry logic with exponential backoff for transient errors:

```python
from poke_api import Poke

# Default behavior: 2 retries, 10s timeout, 0.3s base backoff
client = Poke()

# Override per-request
pokemon = client.pokemon.get(1, timeout=30.0, retries=5, backoff=0.5)

# Async usage
from poke_api import AsyncPoke
async_client = AsyncPoke()
result = await async_client.pokemon.get("pikachu", retries=3, timeout=15.0)
```

**Retry behavior:**
- Retries server errors (5xx status codes) and network errors
- Uses exponential backoff: `backoff * (2 ** attempt)`
- Default: 2 retries, 0.3s base backoff, 10s timeout
- Per-request overrides via `timeout=`, `retries=`, `backoff=` kwargs

## Error Handling

## Testing

The SDK includes both unit tests (with mocked HTTP calls) and integration tests (hitting the real PokeAPI).

### Run All Tests

Using Makefile:

```bash
make test
```
Using poetry directly:
```bash
# All tests (unit + integration)
poetry run pytest

# Only unit tests (fast, no network calls)
poetry run pytest tests/test_pokemon_unit.py

# Only integration tests (hits real API)
poetry run pytest -m integration

# Verbose output
poetry run pytest -v
```

### Test Types

- **Unit tests** (`tests/test_*_unit.py`): Mock HTTP calls to test retry logic, error handling, and client behavior
- **Integration tests** (`tests/test_integration.py`): Hit the real PokeAPI to verify end-to-end functionality

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup and guidelines. This project uses conventional commits for automated versioning and PyPI publishing.

## License

Licensed under the [MIT license](./LICENSE).

Copyright (c) 2025 Patrick Prunty