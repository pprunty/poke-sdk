"""Pokemon-related Pydantic models."""

from __future__ import annotations
from typing import List, Optional, Dict, Any
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
    version_details: List[VersionDetail]


class VersionDetail(BaseModel):
    """Version-specific item details."""

    rarity: int
    version: NamedResource


class MoveLearnMethod(BaseModel):
    """How a Pokemon learns a move."""

    name: str
    url: str


class VersionGroup(BaseModel):
    """Version group information."""

    name: str
    url: str


class VersionGroupDetail(BaseModel):
    """Version group specific move learning details."""

    level_learned_at: int
    move_learn_method: MoveLearnMethod
    order: Optional[int]
    version_group: VersionGroup


class Move(BaseModel):
    """Pokemon move information."""

    move: NamedResource
    version_group_details: List[VersionGroupDetail]


class PastAbility(BaseModel):
    """Past generation ability information."""

    abilities: List[Ability]
    generation: NamedResource


class PokemonType(BaseModel):
    """Pokemon type information."""

    slot: int
    type: NamedResource


class PastType(BaseModel):
    """Past generation type information."""

    generation: NamedResource
    types: List[PokemonType]


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
    other: Optional[Dict[str, Any]] = None
    versions: Optional[Dict[str, Any]] = None


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

    abilities: List[Ability] = Field(default_factory=list)
    cries: Optional[Cries] = None
    forms: List[NamedResource] = Field(default_factory=list)
    game_indices: List[GameIndex] = Field(default_factory=list)
    held_items: List[HeldItem] = Field(default_factory=list)
    moves: List[Move] = Field(default_factory=list)
    past_abilities: List[PastAbility] = Field(default_factory=list)
    past_types: List[PastType] = Field(default_factory=list)
    species: NamedResource
    sprites: Optional[Sprites] = None
    stats: List[Stat] = Field(default_factory=list)
    types: List[PokemonType] = Field(default_factory=list)


# Pagination models
class PokemonList(BaseModel):
    """Pokemon list response."""

    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[NamedResource] = Field(default_factory=list)
