"""PokeAPI type definitions."""

from .._types import BaseModel, NamedResource, Name
from .pokemon import (
    Pokemon,
    PokemonList,
    Ability,
    Sprites,
    Stat,
    PokemonType,
    Move,
    GameIndex,
    HeldItem,
    Cries,
)
from .generation import Generation, GenerationList

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
