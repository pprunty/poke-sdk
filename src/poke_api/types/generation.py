"""Generation-related Pydantic models."""

from typing import List, Optional
from pydantic import Field

from .._types import BaseModel, NamedResource, Name


class Generation(BaseModel):
    """Complete Generation model."""

    id: int
    name: str
    main_region: NamedResource

    abilities: List[NamedResource] = Field(default_factory=list)
    moves: List[NamedResource] = Field(default_factory=list)
    names: List[Name] = Field(default_factory=list)
    pokemon_species: List[NamedResource] = Field(default_factory=list)
    types: List[NamedResource] = Field(default_factory=list)
    version_groups: List[NamedResource] = Field(default_factory=list)


# Pagination models
class GenerationList(BaseModel):
    """Generation list response."""

    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[NamedResource] = Field(default_factory=list)
