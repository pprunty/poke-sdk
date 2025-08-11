# PokeAPI Python API Library

![header](./header.png)

The PokeAPI Python Library provides access to [PokeAPI](https://pokeapi.co/) APIs from Python 3.8 applications (haven't tested on other versions). The library includes type definitions for all APIs, including request params and response fields, and offers both synchronous and asynchronous clients powered by httpx.

Thanks to [PokeAPI](https://pokeapi.co/) for maintaining and making the APIs publicly accessible.

## Documentation

The REST API documentation can be found at <pokeapi.co/docs>. The live site crashes... always. But the APIs are pretty reliable.

## Requirements

* python 3.8

## Installation

### pip

```
pip install poke_sdk
```

> Note: I haven't pushed this to pip (yet). Follow instructions below for manual installation

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
pikachu = client.pokemon.get("pikachu")
print(pikachu)
# Output: Pokemon(id=25, name='pikachu', lists={abilities: 2, forms: 1, moves: 105, types: 1})

# List Pokemon with pagination
pokemon_list = client.pokemon.list(limit=5, offset=10)
print(pokemon_list)
# Output: PokemonList(lists={results: 5})
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

> Warning: The 

## Project Structure

```bash

```

## Pagination

## Caching

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