"""Pokedex-related Pydantic models for rankings and detail views."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from .._types import BaseModel


class PokedexRankRow(BaseModel):
    """A row in the pokedex rankings table."""
    
    rank: int
    regional_no: Optional[int] = None  # entry number in the provided pokedex
    national_no: int                   # species.id
    name: str
    types: list[str] = Field(default_factory=list)  # ["psychic"] or ["psychic","ice"]
    base_stats: dict[str, int] = Field(default_factory=dict)  # {"hp":106,"attack":110,...}
    total_base_stat: int
    sprite_url: Optional[str] = None


class LocalizedName(BaseModel):
    """Multilingual name representation."""
    
    language: str
    value: str


class DamageTakenEntry(BaseModel):
    """Type effectiveness multiplier entry."""
    
    type: str
    multiplier: float  # 0, 0.25, 0.5, 1, 2, 4


class EVYield(BaseModel):
    """Effort Value yield for a stat."""
    
    stat: str
    value: int


class MoveLearn(BaseModel):
    """Move learning information."""
    
    level: Optional[int] = None  # None for TM/HM/Tutor/Egg
    name: str
    type: Optional[str] = None
    power: Optional[int] = None
    accuracy: Optional[int] = None
    pp: Optional[int] = None
    method: str  # "level-up" | "machine" | "tutor" | "egg"
    version_group: str


class LocationEntry(BaseModel):
    """Location encounter information."""
    
    version: str
    location_area: str


class PokedexDetailView(BaseModel):
    """Complete Pokemon detail view (Serebii-style)."""
    
    name: str
    other_names: list[LocalizedName] = Field(default_factory=list)
    national_no: int
    regional_no: Optional[int] = None
    gender_ratio: str  # "M 87.5% / F 12.5%" or "Genderless"
    types: list[str] = Field(default_factory=list)
    classification: Optional[str] = None  # genus (en)
    height_m: float
    height_ft_in: str  # "6'07\""
    weight_kg: float
    weight_lbs: float
    capture_rate: int
    base_egg_steps: int
    growth_rate: str
    base_happiness: int
    ev_yields: list[EVYield] = Field(default_factory=list)
    damage_taken: list[DamageTakenEntry] = Field(default_factory=list)
    wild_held_items: dict[str, list[str]] = Field(default_factory=dict)  # version -> [items]
    egg_groups: list[str] = Field(default_factory=list)
    evolution_chain: list[str] = Field(default_factory=list)  # species names in order
    locations: list[LocationEntry] = Field(default_factory=list)
    level_up_moves: list[MoveLearn] = Field(default_factory=list)
    tm_hm_moves: list[MoveLearn] = Field(default_factory=list)
    tutor_moves: list[MoveLearn] = Field(default_factory=list)
    gen1_only_moves: list[MoveLearn] = Field(default_factory=list)  # moves present in Gen 1 not in target gen
    sprite_url: Optional[str] = None