# PokeAPI Python API Library

<!-- [![PyPI version](https://badge.fury.io/py/poke-sdk.svg)](https://badge.fury.io/py/poke-sdk) -->

![header](./header.png)

The PokeAPI Python Library provides access to [PokeAPI](https://pokeapi.co/) APIs from Python 3.8 applications (haven't tested on other versions). The library includes type definitions for its two core APIs (`/pokemon/{id or name}` and `/generation/{id or name}`), including request params and response fields, and offers both synchronous and asynchronous clients, pagination (with lazy loading), and custom caching and retries powered by httpx, cachetools and pydantic libraries.

Thanks to [PokeAPI](https://pokeapi.co/) for maintaining and making the APIs publicly accessible.

## Documentation

The REST API documentation can be found at <pokeapi.co/docs>. The live site crashes... always. But the APIs are pretty reliable.

## Requirements

* python 3.8
* [Poetry](https://python-poetry.org/) python dependency and project manager (`curl -sSL https://install.python-poetry.org | python3 -` or `pip install poetry`)

## Installation

### Development

```bash
git clone https://github.com/pprunty/poke-sdk.git && cd poke-sdk
```

```bash
make install
```

**Run examples**:

```bash
make example <example_file_path> 
```
The file path should start with `examples/*`

<!-- ### pip

> [!NOTE]
> I haven't pushed this to PyPi (yet)

```bash
pip install poke_sdk
``` -->

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


## Pagination

List methods in the PokeAPI are paginated.

This library provides auto-paginating iterators with each list response, so you do not have to request successive pages manually:

```python
from poke_api import Poke

client = Poke()

all_pokemon = []
# Automatically fetches more pages as needed.
# Note: This will fetch ALL Pokemon (1300+) - use limit for demos
for pokemon in client.pokemon.list():  # Limit for demo
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

Cache settings can be controlled both globally and per-request:

#### Global Cache Access (Advanced)
```python
# Access cache directly (advanced usage)
cache = client.pokemon._cache
print(f"Cache size: {len(cache)} items")
print(f"Cache info: {cache.currsize}/{cache.maxsize} items")

# Clear cache if needed
cache.clear()
```

#### Per-Request Cache Control
```python
# Control caching per request (recommended approach)
pokemon = client.pokemon.get("pikachu", force_refresh=True)      # Skip cache
pokemon = client.pokemon.get("pikachu", use_cache=False)         # Disable caching
pokemon = client.pokemon.get("pikachu", cache_ttl=300)           # Custom TTL

# See "Cache Control" section below for full details
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

## Cache Control

In addition to the automatic caching described above, you can control caching behavior on a per-request basis with cache control parameters:

```python
from poke_api import Poke

client = Poke()

# Force refresh - bypass cache entirely
fresh_data = client.pokemon.get("pikachu", force_refresh=True)

# Disable caching for this request only
no_cache = client.pokemon.get("pikachu", use_cache=False)

# Custom cache TTL (Note: limited support due to single cache instance)
longer_cache = client.pokemon.get("pikachu", cache_ttl=300)  # 5 minutes

# Combine with retry/timeout parameters
robust_request = client.pokemon.get(
    "pikachu",
    force_refresh=True,    # Skip cache
    timeout=30.0,          # 30 second timeout
    retries=3,             # 3 retry attempts
    backoff=1.0            # 1 second base backoff
)
```

### Cache Control Parameters

- **`use_cache`** (bool, default: True): Whether to use caching at all
- **`force_refresh`** (bool, default: False): Force a fresh API call, bypassing cache
- **`cache_ttl`** (int, default: None): Custom cache TTL in seconds (limited support)

### Async Cache Control

The same parameters work with async methods:

```python
import asyncio
from poke_api import AsyncPoke

async def example():
    client = AsyncPoke()
    
    try:
        # Force refresh with async
        fresh = await client.pokemon.get("pikachu", force_refresh=True)
        
        # Disable cache with custom timeout
        result = await client.pokemon.get(
            "pikachu", 
            use_cache=False, 
            timeout=15.0
        )
        
        # List with cache control
        pages = await client.pokemon.list(
            limit=50,
            force_refresh=True,  # Always get fresh data
            timeout=20.0
        )
        
    finally:
        await client.aclose()

asyncio.run(example())
```

### Cache Control Best Practices

1. **Use `force_refresh=True`** when you need the most recent data (e.g., after creating/updating resources)
2. **Use `use_cache=False`** for one-time requests where caching doesn't provide value
3. **Combine with retries** for critical requests: `force_refresh=True, retries=3`
4. **Consider cache TTL** limitations: the current implementation uses a single cache instance per resource

> [!NOTE]
> Custom `cache_ttl` has limitations in the current implementation as all resources share the same TTL cache instance. For different TTL requirements, consider using `force_refresh=True` or `use_cache=False` instead.

## Error Handling

The SDK provides a comprehensive exception hierarchy for handling API errors gracefully. All exceptions inherit from `PokeAPIError` and map HTTP status codes to specific exception types.

### Exception Types

```python
from poke_api import (
    PokeAPIError,           # Base exception for all SDK errors
    APIConnectionError,     # Network/transport problems
    APITimeoutError,        # Request timeouts
    NotFoundError,          # 404 Not Found
    BadRequestError,        # 400 Bad Request  
    RateLimitError,         # 429 Too Many Requests
    ServerError,            # 5xx Server Errors
)
```

### Automatic Error Mapping

The SDK automatically maps HTTP status codes to appropriate exceptions using the `map_http_error()` method:

- **4xx Client Errors**: `BadRequestError`, `NotFoundError`, `RateLimitError`, etc.
- **5xx Server Errors**: `ServerError`, `ServiceUnavailableError`
- **Network Issues**: `APIConnectionError`, `APITimeoutError`

### Usage Examples

```python
from poke_api import Poke, NotFoundError, APIConnectionError

client = Poke()

try:
    # This will raise NotFoundError for non-existent Pokemon
    pokemon = client.pokemon.get("definitely-not-a-pokemon")
except NotFoundError:
    print("Pokemon not found!")
except APIConnectionError:
    print("Network error - check your connection")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Error Information

All API errors include the HTTP status code and response body when available:

```python
try:
    pokemon = client.pokemon.get("invalid-pokemon")
except NotFoundError as e:
    print(f"Status code: {e.status_code}")  # 404
    print(f"Error message: {e}")            # Details from API
```

## Testing

The SDK includes both unit tests (with mocked HTTP calls) and integration tests (hitting the real PokeAPI).

### Run All Tests

Using Makefile:

```bash
make test
```
This will include a test coverage report.

### Test Types

- **Unit tests** (`tests/test_*_unit.py`): Mock HTTP calls to test retry logic, error handling, and client behavior
- **Integration tests** (`tests/test_integration.py`): Hit the real PokeAPI to verify end-to-end functionality

## Contributing

See [Conribution Guidelines](./CONTRIBUTING.md) for development setup and guidelines. This project uses conventional commits for automated versioning and PyPI publishing.

## License

Licensed under the [MIT license](./LICENSE).

Copyright (c) 2025 Patrick Prunty