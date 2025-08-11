"""PokeAPI type definitions."""

from .._types import BaseModel, Name, NamedResource
from .generation import Generation, GenerationList
from .pokemon import (
    Ability,
    Cries,
    GameIndex,
    HeldItem,
    Move,
    Pokemon,
    PokemonList,
    PokemonType,
    Sprites,
    Stat,
)

__all__ = [
    # Base types
    "BaseModel",
    "NamedResource",
    "Name",
    # Pokemon types
    "Pokemon",
    "PokemonList",
    "Ability",
    "Sprites",
    "Stat",
    "PokemonType",
    "Move",
    "GameIndex",
    "HeldItem",
    "Cries",
    # Generation types
    "Generation",
    "GenerationList",
]
