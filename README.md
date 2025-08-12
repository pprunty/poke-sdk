# PokeAPI Python API Library

[![PyPI version](https://badge.fury.io/py/poke-sdk.svg)](https://badge.fury.io/py/poke-sdk)

![header](./header.png)

The PokeAPI Python Library provides access to [PokeAPI](https://pokeapi.co/) APIs from Python 3.8+ applications. The library includes type definitions for PokeAPI endpoints (`/pokemon/{id or name}` and `/generation/{id or name}`), plus custom high-level resources built on top of the API for enhanced functionality. The library also offers both synchronous and asynchronous clients, pagination (with lazy loading), and custom caching and retries powered by httpx, cachetools and pydantic libraries.

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

or:

```bash
poetry install
```

**Run examples**:

```bash
make example <example_file_path> 
```
The file path should start with `examples/*`

### pip

> [!WARNING]
> This package has not been published to PyPI yet. Use the development installation method above.

```bash
pip install poke-sdk
```

## Usage

```python
from poke_api import Poke

client = Poke()

# Get a Pokemon by ID or name
pikachu = client.pokemon.get(id=25)
print(pikachu)
# Output: Pokemon(id=25, name='pikachu', lists={abilities: 2, forms: 1, moves: 105, types: 1})
```

## Async Usage

```python
from poke_api import AsyncPoke

client = AsyncPoke()

async def main() -> None:
    pikachu = await client.pokemon.get(name="pikachu")
    print(pikachu)
```

## Resources

### Core API Resources
Direct wrappers around PokeAPI endpoints:

- **`client.pokemon.get/list()`**: `/pokemon/{id or name}` - Individual Pokemon data
- **`client.generation.get/list()`**: `/generation/{id or name}` - Generation information

These resources are subclasses which inherit from the `[BaseResource](./src/poke_api/_resource.py)`.

### Custom Resources
High-level functionality built on top of the PokeAPI:

- **`client.pokedex.detail/ranking()`**: Comprehensive Pokemon views with rankings and detailed information (like [serebii.net](https://serebii.net/pokedex))
- **`client.search.pokemon/generation().`**: Cross-resource search capabilities

Note: The `pokedex` and `search` custom resources are not based on the `[BaseResource](./src/poke_api/_resource.py)` and therefore do not inherit methods for `list` and `get`.

## Object Representation

All models inherit from `BaseModel` and provide:
* `.to_dict()` - Convert to dictionary representation
* `.to_json()` - Convert to JSON string representation
* `.summary()` - Multi-line pretty summary

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

### Link Expansion (Optional)

`expand` resolves selected `name/url` references into full objects, bounded by depth and max requests.
It returns a **dict copy** of your model, leaving the original model untouched. Expanded refs store data
under a reserved `__expanded__` key.

```python
# Async example
from poke_api import AsyncPoke

client = AsyncPoke()

async def main():
    # Get a Pokemon 
    bulba = await client.pokemon.get("bulbasaur")
    
    # Expand the first move reference to get full move data
    expanded = await client.expand(
        bulba, 
        paths=["moves.move"],  # Only expand move references in the moves array
        depth=1, 
        max_requests=50, 
        concurrency=6
    )
    
    # Access expanded data via __expanded__ key
    first_move = expanded["moves"][0]["move"]
    print(first_move["name"])  # -> "razor-wind" (original name)
    print(first_move["__expanded__"]["name"])  # -> "razor-wind" (full move data name)
    print(first_move["__expanded__"]["power"])  # -> 80 (move power from expanded data)

# Sync example  
from poke_api import Poke

with Poke() as client:
    bulba = client.pokemon.get("bulbasaur")
    expanded = client.expand(
        bulba, 
        paths=["moves.move"], 
        depth=1, 
        max_requests=50
    )
    
    # Same access pattern
    move_data = expanded["moves"][0]["move"]["__expanded__"]
    print(f"Move: {move_data['name']}, Power: {move_data.get('power', 'N/A')}")
```

**Key Features:**
- **Non-invasive**: Original models are never modified
- **Path filtering**: Use `paths=["moves.move", "species"]` to target specific references
- **Depth control**: `depth=2` will expand references within expanded data
- **Request budgeting**: `max_requests=100` prevents runaway API usage
- **Async concurrency**: `concurrency=6` controls parallel requests
- **Automatic deduplication**: Same URLs are only fetched once
- **Cache integration**: Uses existing client caching and retry logic

**Usage Notes:**
- Use small `max_requests` and `concurrency` values to be API-friendly
- Expansion is breadth-first by depth level  
- The `__expanded__` key is reserved - avoid using it in your data
- Data is read via the client's normal request layer (benefits from caching, retries, error handling)

### Pokedex (serebii like views)

> **Note**: This is a custom resource built on top of the PokeAPI, not a direct endpoint wrapper. It combines multiple API calls to provide Serebii-style comprehensive Pokemon views.


Comprehensive Pokedex data with rankings tables and detailed Pokemon views. Inspired by views seen on [serebii.net pokedex](https://serebii.net/pokedex).

#### Rankings:

```python
from poke_api import AsyncPoke, Poke

johto_rankings = await client.pokedex.rankings(generation=2) # sort_by="total" default
data = [p.to_dict() for p in johto_rankings]
print(json.dumps(data, indent=2, ensure_ascii=False))
```

Example ranking output:

```json
[
  {
    "rank": 1,
    "regional_no": 247,
    "national_no": 249,
    "name": "lugia",
    "types": [
      "psychic",
      "flying"
    ],
    "base_stats": {
      "hp": 106,
      "attack": 90,
      "defense": 130,
      "special-attack": 90,
      "special-defense": 154,
      "speed": 110
    },
    "total_base_stat": 680,
    "sprite_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-ii/gold/249.png"
  },
  {
    "rank": 2,
    "regional_no": 248,
    "national_no": 250,
    "name": "ho-oh",
    "types": [
      "fire",
      "flying"
    ],
    "base_stats": {
      "hp": 106,
      "attack": 130,
      "defense": 90,
      "special-attack": 110,
      "special-defense": 154,
      "speed": 90
    },
    "total_base_stat": 680,
    "sprite_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-ii/gold/250.png"
  },
  {
    "rank": 3,
    "regional_no": 249,
    "national_no": 150,
    "name": "mewtwo",
    "types": [
      "psychic"
    ],
    "base_stats": {
      "hp": 106,
      "attack": 110,
      "defense": 90,
      "special-attack": 154,
      "special-defense": 90,
      "speed": 130
    },
    "total_base_stat": 680,
    "sprite_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-ii/gold/150.png"
  },
  {
    "rank": 4,
    "regional_no": 243,
    "national_no": 149,
    "name": "dragonite",
    "types": [
      "dragon",
      "flying"
    ],
    "base_stats": {
      "hp": 91,
      "attack": 134,
      "defense": 95,
      "special-attack": 100,
      "special-defense": 100,
      "speed": 80
    },
    "total_base_stat": 600,
    "sprite_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-ii/gold/149.png"
  },
  {
    "rank": 5,
    "regional_no": 246,
    "national_no": 248,
    "name": "tyranitar",
    "types": [
      "rock",
      "dark"
    ],
    "base_stats": {
      "hp": 100,
      "attack": 134,
      "defense": 110,
      "special-attack": 95,
      "special-defense": 100,
      "speed": 61
    },
    "total_base_stat": 600,
    "sprite_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-ii/gold/248.png"
  },
...
]
```

#### Detail:


```python
from poke_api import AsyncPoke, Poke

# Get by number
mewtwo_detail = await client.pokedex.detail(generation=1, number=150)

# Get by name
mewtwo_detail = await client.pokedex.detail(generation=1, name="mewtwo")

print(mewtwo_detail.to_json())
```

Example detail output: 

```json
{
  "name": "mewtwo",
  "other_names": [
    {"language": "ja-Hrkt", "value": "ミュウツー"},
    {"language": "ko", "value": "뮤츠"},
    {"language": "zh-Hant", "value": "超夢"},
    {"language": "fr", "value": "Mewtwo"},
    {"language": "de", "value": "Mewtu"},
    ...
  ],
  "national_no": 150,
  "regional_no": 150,
  "gender_ratio": "Genderless",
  "types": ["psychic"],
  "classification": "Genetic Pokémon",
  "height_m": 2.0,
  "height_ft_in": "6'07\"",
  "weight_kg": 122.0,
  "weight_lbs": 269.0,
  "capture_rate": 3,
  "base_egg_steps": 30855,
  "growth_rate": "slow",
  "base_happiness": 0,
  "ev_yields": [{"stat": "special-attack", "value": 3}],
  "damage_taken": [
    {"type": "fighting", "multiplier": 0.5},
    {"type": "bug", "multiplier": 2.0},
    {"type": "ghost", "multiplier": 2.0},
    {"type": "psychic", "multiplier": 0.5},
    {"type": "dark", "multiplier": 2.0},
    ...
  ],
  "wild_held_items": {},
  "egg_groups": ["no-eggs"],
  "evolution_chain": ["mewtwo"],
  "locations": [],
  "level_up_moves": [
    {
      "level": 1,
      "name": "confusion",
      "type": "psychic",
      "power": 50,
      "accuracy": 100,
      "pp": 25,
      "method": "level-up",
      "version_group": "red-blue"
    },
    {
      "level": 1,
      "name": "psychic",
      "type": "psychic",
      "power": 90,
      "accuracy": 100,
      "pp": 10,
      "method": "level-up",
      "version_group": "red-blue"
    },
    ...
  ],
  "tm_hm_moves": [
    {
      "level": null,
      "name": "ice-beam",
      "type": "ice",
      "power": 90,
      "accuracy": 100,
      "pp": 10,
      "method": "machine",
      "version_group": "red-blue"
    },
    {
      "level": null,
      "name": "thunderbolt",
      "type": "electric",
      "power": 90,
      "accuracy": 100,
      "pp": 15,
      "method": "machine",
      "version_group": "red-blue"
    },
    ...
  ],
  "tutor_moves": [],
  "gen1_only_moves": [],
  "sprite_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-i/red-blue/150.png",
  "shiny_sprite_url": null
}
```

**Key Improvements in Detail View:**
- **Complete Move Information**: Now includes power, accuracy, PP, and type for all moves
- **Generation-Specific Data**: Only shows moves and locations available in the target generation
- **Shiny Sprites**: Includes `shiny_sprite_url` for generations that support them (Gen 2+)
- **Authentic Experience**: Each generation shows only the data that was actually available in those games

> **Note**: Examples use `...` to indicate where additional data would appear in the full response.

### Search - Cross-Resource Discovery

> **Note**: This is a custom resource that searches across multiple PokeAPI endpoints, not a direct API wrapper.

The search functionality provides filtered search across Pokemon with various criteria:

```python
from poke_api import Poke

client = Poke()

# Search by type
ground_pokemon = client.search.pokemon(type="ground", limit=5)
print(f"Found {ground_pokemon.count} ground-type Pokemon")
for pokemon in ground_pokemon.results:
    print(f"  - {pokemon.name}")

# Search by ability
sand_veil_pokemon = client.search.pokemon(ability="sand-veil", limit=3)
for pokemon in sand_veil_pokemon.results:
    print(f"  - {pokemon.name}")

# Combined search (type + ability)
combined = client.search.pokemon(type="ground", ability="sand-veil")
for pokemon in combined.results:
    print(f"  - {pokemon.name}")
```

**Async usage:**
```python
from poke_api import AsyncPoke

async def main():
    async with AsyncPoke() as client:
        # Search by type with limit
        fire_pokemon = await client.search.pokemon(type="fire", limit=5)
        print(f"Search results: {fire_pokemon}")
        
        # Access individual results
        for pokemon in fire_pokemon.results:
            print(f"  - {pokemon.name}")
            
        # Get full details for a specific result
        detailed = await client.pokemon.get(fire_pokemon.results[0].name)
        print(f"Full details: {detailed.summary()}")

asyncio.run(main())
```

**Available search filters:**
- `type`: Filter by Pokemon type (e.g., "fire", "water", "psychic")
- `ability`: Filter by ability (e.g., "sand-veil", "levitate")
- `limit`: Maximum number of results to return
- Combine multiple filters for precise searches

## Caching

The SDK uses an in-memory **TTL cache** (via [cachetools](https://github.com/tkem/cachetools/)) to speed up repeat calls and reduce traffic to PokéAPI.

### Defaults

* **type**: Per-resource TTL cache (e.g., client.pokemon, client.generation each keep their own cache)
* **Size**: 1024 items per resource
* **TTL**: 60 seconds per entry


```python
from poke_api import Poke

client = Poke()

# First call hits the API
pikachu_1 = client.pokemon.get("pikachu")   # ~200ms

# Within 60s, this is a cache hit
pikachu_2 = client.pokemon.get("pikachu")   # ~1ms
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

### Per-request Cache Controls Controls

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

## Project Structure

```bash
.
├── src/poke_api/               # Main SDK package
│   ├── _client.py              # Sync/async HTTP clients with retry logic
│   ├── _exceptions.py          # SDK exception hierarchy
│   ├── _resource.py            # Base resource classes with caching
│   ├── _types.py               # Common types and BaseModel with friendly printing
│   ├── pagination.py           # Page/AsyncPage classes with auto-iteration
│   ├── expansion.py            # For handling subsequent APIs for NamedResources (name+url return objects)
│   ├── resources/              # API resource implementations (pokemon, generation, search, pokedex)
│   └── types/                  # Pydantic models for API responses
├── tests/                      # Unit and integration tests
├── examples/                   # Usage examples organized by resource type
├── pyproject.toml              # Poetry config and dependencies
└── README.md                   # Documentation
```

## Testing

The SDK includes both unit tests (with mocked HTTP calls) and integration tests (hitting the real PokeAPI).

### Run All Tests

```bash
make test
```
This will include a test coverage report.

### Test Types

- **Unit tests** (`tests/test_*_unit.py`): Mock HTTP calls to test retry logic, error handling, and client behavior
- **Integration tests** (`tests/test_integration.py`): Hit the real PokeAPI to verify end-to-end functionality

## Contributing

See [Conribution Guidelines](./CONTRIBUTING.md) for development setup and guidelines. This project uses conventional commits for automated versioning and PyPI publishing.

## Known issues

The static type checker has many issues, I'll get around to fixing them eventually.

To run the check:

```bash
poetry run mypy src/poke_api --ignore-missing-imports
```

## License

Licensed under the [MIT license](./LICENSE).

Copyright (c) 2025 Patrick Prunty