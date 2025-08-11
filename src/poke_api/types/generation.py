"""Generation-related Pydantic models."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from .._types import BaseModel, Name, NamedResource


class Generation(BaseModel):
    """Complete Generation model."""

    id: int
    name: str
    main_region: NamedResource

    abilities: list[NamedResource] = Field(default_factory=list)
    moves: list[NamedResource] = Field(default_factory=list)
    names: list[Name] = Field(default_factory=list)
    pokemon_species: list[NamedResource] = Field(default_factory=list)
    types: list[NamedResource] = Field(default_factory=list)
    version_groups: list[NamedResource] = Field(default_factory=list)


# Pagination models
class GenerationList(BaseModel):
    """Generation list response."""

    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: list[NamedResource] = Field(default_factory=list)
