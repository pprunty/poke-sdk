"""Base models for PokeAPI types."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class BaseModel(PydanticBaseModel):
    """Base model with common configuration and friendly printing."""

    model_config = ConfigDict(
        # Allow extra fields for forward compatibility
        extra="ignore",
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Validate assignment
        validate_assignment=True,
    )

    def __repr__(self) -> str:
        """Friendly representation showing key fields and list counts."""
        return self._friendly_repr()

    def __str__(self) -> str:
        """Same as repr for consistent friendly printing."""
        return self._friendly_repr()

    def _friendly_repr(self) -> str:
        """Build friendly representation showing all scalar fields and list counts."""
        # Priority fields to show first (in order)
        priority_fields = ("id", "name")

        # Collect all scalar fields (non-list, non-complex objects)
        scalar_fields = []
        list_counts = {}

        # First add priority fields
        for field_name in priority_fields:
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if isinstance(value, str) and len(value) > 50:
                    value = f'"{value[:47]}..."'
                else:
                    value = repr(value)
                scalar_fields.append(f"{field_name}={value}")

        # Then add all other fields
        for field_name in self.model_fields:
            if field_name not in priority_fields and hasattr(self, field_name):
                field_val = getattr(self, field_name)

                if isinstance(field_val, list):
                    # Lists: only show count if non-empty
                    if len(field_val) > 0:
                        list_counts[field_name] = len(field_val)
                elif not isinstance(field_val, BaseModel) and field_val is not None:
                    # Scalar fields: show all non-None values
                    if isinstance(field_val, str):
                        if len(field_val) > 50:
                            value = f'"{field_val[:47]}..."'
                        else:
                            value = repr(field_val)
                    else:
                        value = repr(field_val)
                    scalar_fields.append(f"{field_name}={value}")
                elif isinstance(field_val, BaseModel):
                    # Nested BaseModel objects: show just class name, not full repr
                    scalar_fields.append(
                        f"{field_name}={field_val.__class__.__name__}(...)"
                    )

        # Build final representation
        parts = scalar_fields.copy()
        if list_counts:
            list_str = ", ".join(f"{k}: {v}" for k, v in list_counts.items())
            parts.append(f"lists={{{list_str}}}")

        return f"{self.__class__.__name__}({', '.join(parts)})"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return self.model_dump()

    def to_json(self, **kwargs) -> str:
        """Convert to JSON string representation."""
        return self.model_dump_json(**kwargs)

    def summary(self) -> str:
        """Multi-line pretty summary (optional detailed view)."""
        lines = [f"{self.__class__.__name__}:"]

        # Show key fields
        for field_name in ("id", "name", "height", "weight", "base_experience"):
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                lines.append(f"  {field_name}: {value}")

        # Show list counts
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, list) and len(field_value) > 0:
                lines.append(f"  {field_name}: {len(field_value)} items")

        return "\n".join(lines)


class NamedResource(BaseModel):
    """Represents a named resource with name and URL."""

    name: str
    url: str


# Alias for search results - same structure as NamedResource
NamedAPIResource = NamedResource


class NamedAPIResourceList(BaseModel):
    """List of named API resources with pagination info."""

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[NamedAPIResource]


class Name(BaseModel):
    """Multi-language name representation."""

    language: NamedResource
    name: str


class Language(BaseModel):
    """Language information."""

    name: str
    url: str


class Region(BaseModel):
    """Region information."""

    name: str
    url: str
