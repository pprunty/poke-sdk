"""Pokemon-related Pydantic models."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from .._types import BaseModel, NamedResource


class Ability(BaseModel):
    """Pokemon ability information."""

    ability: Optional[NamedResource] = None
    is_hidden: bool
    slot: int


class Cries(BaseModel):
    """Pokemon cry audio URLs."""

    latest: str
    legacy: str


class GameIndex(BaseModel):
    """Pokemon game index information."""

    game_index: int
    version: NamedResource


class HeldItem(BaseModel):
    """Pokemon held item information."""

    item: NamedResource
    version_details: list[VersionDetail]


class VersionDetail(BaseModel):
    """Version-specific item details."""

    rarity: int
    version: NamedResource




class VersionGroupDetail(BaseModel):
    """Version group specific move learning details."""

    level_learned_at: int
    move_learn_method: NamedResource
    order: Optional[int]
    version_group: NamedResource


class Move(BaseModel):
    """Pokemon move information."""

    move: NamedResource
    version_group_details: list[VersionGroupDetail]


class PastAbility(BaseModel):
    """Past generation ability information."""

    abilities: list[Ability]
    generation: NamedResource


class PokemonType(BaseModel):
    """Pokemon type information."""

    slot: int
    type: NamedResource


class PastType(BaseModel):
    """Past generation type information."""

    generation: NamedResource
    types: list[PokemonType]


class Sprites(BaseModel):
    """Pokemon sprite URLs."""

    back_default: Optional[str] = None
    back_female: Optional[str] = None
    back_shiny: Optional[str] = None
    back_shiny_female: Optional[str] = None
    front_default: Optional[str] = None
    front_female: Optional[str] = None
    front_shiny: Optional[str] = None
    front_shiny_female: Optional[str] = None
    other: Optional[dict[str, Any]] = None
    versions: Optional[dict[str, Any]] = None


class Stat(BaseModel):
    """Pokemon stat information."""

    base_stat: int
    effort: int
    stat: NamedResource


class Pokemon(BaseModel):
    """Complete Pokemon model."""

    id: int
    name: str
    base_experience: Optional[int] = None
    height: int
    weight: int
    is_default: bool = True
    order: int
    location_area_encounters: str

    abilities: list[Ability] = Field(default_factory=list)
    cries: Optional[Cries] = None
    forms: list[NamedResource] = Field(default_factory=list)
    game_indices: list[GameIndex] = Field(default_factory=list)
    held_items: list[HeldItem] = Field(default_factory=list)
    moves: list[Move] = Field(default_factory=list)
    past_abilities: list[PastAbility] = Field(default_factory=list)
    past_types: list[PastType] = Field(default_factory=list)
    species: NamedResource
    sprites: Optional[Sprites] = None
    stats: list[Stat] = Field(default_factory=list)
    types: list[PokemonType] = Field(default_factory=list)


# Pagination models
class PokemonList(BaseModel):
    """Pokemon list response."""

    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: list[NamedResource] = Field(default_factory=list)
