"""Pokedex resource for rankings and detailed Pokemon views."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Union

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._client import AsyncPoke, Poke
from ..types.pokedex import (
    DamageTakenEntry,
    EVYield,
    LocationEntry,
    LocalizedName,
    MoveLearn,
    PokedexDetailView,
    PokedexRankRow,
)


# --- Helper Functions -------------------------------------------------------

def pick_sprite(pokemon_data: Dict[str, Any], pokedex: str, sprite_preference: Optional[str]) -> Optional[str]:
    """Pick the best sprite URL based on pokedex and preference."""
    sprites = pokemon_data.get("sprites", {})
    
    if not sprites:
        return None
    
    # If explicit preference is set, try to find it
    if sprite_preference:
        versions = sprites.get("versions", {})
        for gen_key, gen_data in versions.items():
            if isinstance(gen_data, dict) and sprite_preference in gen_data:
                game_sprites = gen_data[sprite_preference]
                if isinstance(game_sprites, dict) and game_sprites.get("front_default"):
                    return game_sprites["front_default"]
    
    # Auto-derive from pokedex if no explicit preference
    versions = sprites.get("versions", {})
    
    if pokedex == "kanto":
        # Prefer red-blue, fallback to yellow
        for pref in ["red-blue", "yellow"]:
            gen1 = versions.get("generation-i", {})
            if isinstance(gen1, dict) and pref in gen1:
                game_sprites = gen1[pref]
                if isinstance(game_sprites, dict) and game_sprites.get("front_default"):
                    return game_sprites["front_default"]
    
    elif pokedex == "original-johto":
        # Prefer gold/silver, fallback to crystal
        gen2 = versions.get("generation-ii", {})
        if isinstance(gen2, dict):
            for pref in ["gold", "silver", "crystal"]:
                if pref in gen2:
                    game_sprites = gen2[pref]
                    if isinstance(game_sprites, dict) and game_sprites.get("front_default"):
                        return game_sprites["front_default"]
    
    elif pokedex == "updated-johto":
        # Prefer crystal, fallback to gold/silver
        gen2 = versions.get("generation-ii", {})
        if isinstance(gen2, dict):
            for pref in ["crystal", "gold", "silver"]:
                if pref in gen2:
                    game_sprites = gen2[pref]
                    if isinstance(game_sprites, dict) and game_sprites.get("front_default"):
                        return game_sprites["front_default"]
    
    elif pokedex == "hoenn":
        # Prefer ruby/sapphire, fallback to emerald
        gen3 = versions.get("generation-iii", {})
        if isinstance(gen3, dict):
            for pref in ["ruby-sapphire", "emerald"]:
                if pref in gen3:
                    game_sprites = gen3[pref]
                    if isinstance(game_sprites, dict) and game_sprites.get("front_default"):
                        return game_sprites["front_default"]
    
    elif pokedex == "galar":
        # Prefer sword/shield sprites
        gen8 = versions.get("generation-viii", {})
        if isinstance(gen8, dict) and "icons" in gen8:
            icons = gen8["icons"]
            if isinstance(icons, dict) and icons.get("front_default"):
                return icons["front_default"]
    
    # Final fallback to default sprite
    return sprites.get("front_default")


def get_regional_no(species_data: Dict[str, Any], pokedex: str) -> Optional[int]:
    """Extract regional pokedex number for the given pokedex."""
    pokedex_numbers = species_data.get("pokedex_numbers", [])
    for entry in pokedex_numbers:
        if isinstance(entry, dict) and entry.get("pokedex", {}).get("name") == pokedex:
            return entry.get("entry_number")
    return None


def calc_total_base_stat(pokemon_data: Dict[str, Any]) -> int:
    """Calculate total base stat from pokemon data."""
    stats = pokemon_data.get("stats", [])
    total = 0
    for stat_entry in stats:
        if isinstance(stat_entry, dict):
            total += stat_entry.get("base_stat", 0)
    return total


def collect_types(pokemon_data: Dict[str, Any]) -> List[str]:
    """Extract type names from pokemon data."""
    types = []
    type_entries = pokemon_data.get("types", [])
    for type_entry in type_entries:
        if isinstance(type_entry, dict) and "type" in type_entry:
            type_name = type_entry["type"].get("name")
            if type_name:
                types.append(type_name)
    return types


def format_gender_ratio(gender_rate: int) -> str:
    """Format gender ratio from PokéAPI gender_rate."""
    if gender_rate == -1:
        return "Genderless"
    
    female_percent = gender_rate * 12.5
    male_percent = 100 - female_percent
    return f"M {male_percent:.1f}% / F {female_percent:.1f}%"


def calc_egg_steps(hatch_counter: int) -> int:
    """Calculate base egg steps from hatch counter."""
    return 255 * (hatch_counter + 1)


def ft_in(meters: float) -> str:
    """Convert meters to feet and inches format."""
    total_inches = meters * 39.3701
    feet = int(total_inches // 12)
    inches = round(total_inches % 12)
    return f"{feet}'{inches:02d}\""


def kg_to_lbs(kg: float) -> float:
    """Convert kilograms to pounds."""
    return round(kg * 2.20462, 1)


def flatten_evolution_chain(chain_data: Dict[str, Any]) -> List[str]:
    """Flatten evolution chain into list of species names."""
    def _collect_species(node: Dict[str, Any]) -> List[str]:
        species = []
        if "species" in node and "name" in node["species"]:
            species.append(node["species"]["name"])
        
        for evolution in node.get("evolves_to", []):
            species.extend(_collect_species(evolution))
        
        return species
    
    if "chain" in chain_data:
        return _collect_species(chain_data["chain"])
    return []


def compute_damage_taken(def_types: List[str], type_data_cache: Dict[str, Dict[str, Any]]) -> List[DamageTakenEntry]:
    """Compute damage taken multipliers for all attacking types."""
    # Standard Pokemon types (Gen 1-2 focus)
    all_types = [
        "normal", "fighting", "flying", "poison", "ground", "rock", 
        "bug", "ghost", "steel", "fire", "water", "grass", "electric", 
        "psychic", "ice", "dragon", "dark"
    ]
    
    damage_taken = []
    
    for attacking_type in all_types:
        multiplier = 1.0
        
        for defending_type in def_types:
            type_data = type_data_cache.get(defending_type, {})
            damage_relations = type_data.get("damage_relations", {})
            
            # Check if attacking type does different damage to this defending type
            double_damage_from = [t.get("name") for t in damage_relations.get("double_damage_from", [])]
            half_damage_from = [t.get("name") for t in damage_relations.get("half_damage_from", [])]
            no_damage_from = [t.get("name") for t in damage_relations.get("no_damage_from", [])]
            
            if attacking_type in double_damage_from:
                multiplier *= 2.0
            elif attacking_type in half_damage_from:
                multiplier *= 0.5
            elif attacking_type in no_damage_from:
                multiplier *= 0.0
        
        damage_taken.append(DamageTakenEntry(type=attacking_type, multiplier=round(multiplier, 2)))
    
    return damage_taken


def filter_moves(pokemon_moves: List[Dict[str, Any]], version_group: str, method: str) -> List[Dict[str, Any]]:
    """Filter pokemon moves by version group and learn method."""
    filtered_moves = []
    
    for move_entry in pokemon_moves:
        if not isinstance(move_entry, dict) or "move" not in move_entry:
            continue
        
        move_name = move_entry["move"].get("name")
        if not move_name:
            continue
        
        version_group_details = move_entry.get("version_group_details", [])
        
        for detail in version_group_details:
            if not isinstance(detail, dict):
                continue
            
            detail_vg = detail.get("version_group", {}).get("name")
            detail_method = detail.get("move_learn_method", {}).get("name")
            
            if detail_vg == version_group and detail_method == method:
                level = detail.get("level_learned_at") if method == "level-up" else None
                filtered_moves.append({
                    "name": move_name,
                    "level": level,
                    "version_group": version_group,
                    "method": method
                })
                break  # Only need one match per move
    
    return filtered_moves


def resolve_number(pokedex_entries: List[Dict[str, Any]], number: Union[int, str]) -> str:
    """Resolve regional/national number or name to species identifier."""
    if isinstance(number, str):
        # Assume it's a species name
        return number
    
    # Try to find by regional number first
    for entry in pokedex_entries:
        if isinstance(entry, dict) and entry.get("entry_number") == number:
            return entry.get("pokemon_species", {}).get("name", str(number))
    
    # Fall back to treating as national number
    return str(number)


def filter_sprites_by_generation(sprites: Dict[str, Any], generation: Optional[int] = None) -> Dict[str, Any]:
    """Filter sprites to only include generation-appropriate ones."""
    if generation is None:
        return sprites
    
    # Generation to sprite version mapping
    generation_sprites = {
        1: ["generation-i"],
        2: ["generation-ii"], 
        3: ["generation-iii"],
        4: ["generation-iv"],
        5: ["generation-v"],
        6: ["generation-vi"],
        7: ["generation-vii"],
        8: ["generation-viii"]
    }
    
    allowed_generations = generation_sprites.get(generation, [])
    if not allowed_generations:
        return {
            "front_default": sprites.get("front_default"),
            "front_shiny": sprites.get("front_shiny"),
            "back_default": sprites.get("back_default"), 
            "back_shiny": sprites.get("back_shiny"),
            "versions": {}
        }
    
    # Filter versions to only include allowed generations
    filtered_versions = {}
    versions = sprites.get("versions", {})
    
    for allowed_gen in allowed_generations:
        if allowed_gen in versions:
            filtered_versions[allowed_gen] = versions[allowed_gen]
    
    return {
        "front_default": sprites.get("front_default"),
        "front_shiny": sprites.get("front_shiny"), 
        "back_default": sprites.get("back_default"),
        "back_shiny": sprites.get("back_shiny"),
        "versions": filtered_versions
    }


# --- Resource Classes -------------------------------------------------------

class PokedexResource:
    """Sync Pokedex resource for rankings and detail views."""
    
    def __init__(self, client: Poke) -> None:
        self.client = client
    
    def _resolve_generation_to_pokedex(self, generation: int) -> str:
        """Resolve generation number to main region pokedex name."""
        try:
            # Fetch generation data from API
            response = self.client._request("GET", f"/generation/{generation}")
            generation_data = response.json()
            
            main_region = generation_data.get("main_region")
            if not main_region:
                raise ValueError(f"Generation {generation} has no main region")
            
            region_name = main_region.get("name")
            if not region_name:
                raise ValueError(f"Generation {generation} main region has no name")
            
            # Map region name to appropriate pokedex
            region_to_pokedex = {
                "kanto": "kanto",
                "johto": "original-johto", 
                "hoenn": "hoenn",
                "sinnoh": "sinnoh",  # May not be available
                "unova": "unova",    # May not be available
                "kalos": "central-kalos",  # May not be available
                "alola": "alola",    # May not be available
                "galar": "galar"
            }
            
            pokedex_name = region_to_pokedex.get(region_name)
            if not pokedex_name:
                raise ValueError(f"No pokedex mapping found for region: {region_name}")
            
            return pokedex_name
            
        except Exception as e:
            if "Not Found" in str(e):
                raise ValueError(f"Generation {generation} not found")
            raise ValueError(f"Error resolving generation {generation}: {e}")
    
    def rankings(
        self,
        *,
        pokedex: Optional[str] = None,
        generation: Optional[int] = None,
        sort_by: str = "total",
        sprite_preference: Optional[str] = None,
        concurrency: int = 6,
    ) -> List[PokedexRankRow]:
        """Get rankings table for a pokedex.
        
        Args:
            pokedex: Pokedex identifier (e.g., "national", "kanto", "original-johto", "hoenn", "galar")
                    Mutually exclusive with generation parameter
            generation: Generation number (1-8) to auto-map to main region pokedex
                       Mutually exclusive with pokedex parameter  
            sort_by: Stat to sort by - "total", "hp", "attack", "defense", 
                    "special-attack", "special-defense", "speed"
            sprite_preference: Specific sprite version preference
            concurrency: Number of concurrent requests (sync version ignores this)
        """
        # Validate parameters
        if pokedex is None and generation is None:
            raise ValueError("Either pokedex or generation parameter must be provided")
        if pokedex is not None and generation is not None:
            raise ValueError("pokedex and generation parameters are mutually exclusive")
        
        # Validate sort_by parameter
        valid_stats = {"total", "hp", "attack", "defense", "special-attack", "special-defense", "speed"}
        if sort_by not in valid_stats:
            raise ValueError(f"sort_by must be one of: {', '.join(valid_stats)}")
        
        # Resolve generation to pokedex if needed
        if generation is not None:
            pokedex = self._resolve_generation_to_pokedex(generation)
        
        # Fetch the pokedex entries
        response = self.client._request("GET", f"/pokedex/{pokedex}")
        pokedex_data = response.json()
        
        pokemon_entries = pokedex_data.get("pokemon_entries", [])
        if not pokemon_entries:
            return []
        
        rows = []
        
        for entry in pokemon_entries:
            if not isinstance(entry, dict):
                continue
            
            species_name = entry.get("pokemon_species", {}).get("name")
            regional_no = entry.get("entry_number")
            
            if not species_name:
                continue
            
            # Fetch pokemon data (default variety)
            try:
                pokemon_response = self.client._request("GET", f"/pokemon/{species_name}")
                pokemon_data = pokemon_response.json()
                
                # Get species data for national number
                species_response = self.client._request("GET", f"/pokemon-species/{species_name}")
                species_data = species_response.json()
                
                national_no = species_data.get("id", 0)
                name = species_data.get("name", species_name)
                
                # Build base stats dict
                base_stats = {}
                for stat_entry in pokemon_data.get("stats", []):
                    if isinstance(stat_entry, dict):
                        stat_name = stat_entry.get("stat", {}).get("name", "")
                        base_stat = stat_entry.get("base_stat", 0)
                        if stat_name:
                            base_stats[stat_name] = base_stat
                
                total_base_stat = calc_total_base_stat(pokemon_data)
                types = collect_types(pokemon_data)
                sprite_url = pick_sprite(pokemon_data, pokedex, sprite_preference)
                
                row = PokedexRankRow(
                    rank=0,  # Will be set after sorting
                    regional_no=regional_no,
                    national_no=national_no,
                    name=name,
                    types=types,
                    base_stats=base_stats,
                    total_base_stat=total_base_stat,
                    sprite_url=sprite_url
                )
                
                rows.append(row)
                
            except Exception:
                # Skip Pokemon that can't be fetched
                continue
        
        # Sort by specified stat descending and assign ranks
        if sort_by == "total":
            rows.sort(key=lambda x: x.total_base_stat, reverse=True)
        else:
            rows.sort(key=lambda x: x.base_stats.get(sort_by, 0), reverse=True)
        
        for i, row in enumerate(rows):
            row.rank = i + 1
        
        return rows
    
    def detail(
        self,
        *,
        pokedex: Optional[str] = None,
        generation: Optional[int] = None,
        number: Union[int, str],
        version_group: Optional[str] = None,
        sprite_preference: Optional[str] = None,
        concurrency: int = 6,
    ) -> PokedexDetailView:
        """Get detailed view for a Pokemon."""
        # Validate parameters
        if pokedex is None and generation is None:
            raise ValueError("Either pokedex or generation parameter must be provided")
        if pokedex is not None and generation is not None:
            raise ValueError("pokedex and generation parameters are mutually exclusive")
        
        # Resolve generation to pokedex if needed
        if generation is not None:
            pokedex = self._resolve_generation_to_pokedex(generation)
        
        # Fetch pokedex entries to resolve number
        pokedex_response = self.client._request("GET", f"/pokedex/{pokedex}")
        pokedex_data = pokedex_response.json()
        pokemon_entries = pokedex_data.get("pokemon_entries", [])
        
        species_id = resolve_number(pokemon_entries, number)
        
        # Auto-pick version group if not provided
        if version_group is None:
            if pokedex == "kanto":
                version_group = "red-blue"
            elif pokedex == "original-johto":
                version_group = "gold-silver"
            elif pokedex == "updated-johto":
                version_group = "crystal"
            elif pokedex == "hoenn":
                version_group = "ruby-sapphire"
            elif pokedex == "galar":
                version_group = "sword-shield"
            else:
                version_group = "red-blue"  # fallback
        
        # Fetch core data
        species_response = self.client._request("GET", f"/pokemon-species/{species_id}")
        species_data = species_response.json()
        
        pokemon_response = self.client._request("GET", f"/pokemon/{species_id}")
        pokemon_data = pokemon_response.json()
        
        # Basic info
        name = species_data.get("name", "")
        national_no = species_data.get("id", 0)
        regional_no = get_regional_no(species_data, pokedex)
        
        # Names
        other_names = []
        for name_entry in species_data.get("names", []):
            if isinstance(name_entry, dict):
                lang = name_entry.get("language", {}).get("name", "")
                value = name_entry.get("name", "")
                if lang and value and lang != "en":  # Skip English as it's the main name
                    other_names.append(LocalizedName(language=lang, value=value))
        
        # Physical attributes
        height_m = pokemon_data.get("height", 0) / 10.0
        weight_kg = pokemon_data.get("weight", 0) / 10.0
        height_ft_in = ft_in(height_m)
        weight_lbs = kg_to_lbs(weight_kg)
        
        # Species info
        gender_ratio = format_gender_ratio(species_data.get("gender_rate", -1))
        types = collect_types(pokemon_data)
        
        # Find English genus
        classification = None
        for genus_entry in species_data.get("genera", []):
            if isinstance(genus_entry, dict) and genus_entry.get("language", {}).get("name") == "en":
                classification = genus_entry.get("genus", "")
                break
        
        capture_rate = species_data.get("capture_rate", 0)
        base_egg_steps = calc_egg_steps(species_data.get("hatch_counter", 0))
        growth_rate = species_data.get("growth_rate", {}).get("name", "")
        base_happiness = species_data.get("base_happiness", 0)
        
        # EV yields
        ev_yields = []
        for stat_entry in pokemon_data.get("stats", []):
            if isinstance(stat_entry, dict):
                effort = stat_entry.get("effort", 0)
                if effort > 0:
                    stat_name = stat_entry.get("stat", {}).get("name", "")
                    ev_yields.append(EVYield(stat=stat_name, value=effort))
        
        # Type effectiveness (simplified - fetch type data)
        type_data_cache = {}
        for type_name in types:
            try:
                type_response = self.client._request("GET", f"/type/{type_name}")
                type_data_cache[type_name] = type_response.json()
            except Exception:
                type_data_cache[type_name] = {}
        
        damage_taken = compute_damage_taken(types, type_data_cache)
        
        # Wild held items
        wild_held_items = {}
        for item_entry in pokemon_data.get("held_items", []):
            if isinstance(item_entry, dict):
                item_name = item_entry.get("item", {}).get("name", "")
                if item_name:
                    for version_detail in item_entry.get("version_details", []):
                        if isinstance(version_detail, dict):
                            version = version_detail.get("version", {}).get("name", "")
                            if version:
                                if version not in wild_held_items:
                                    wild_held_items[version] = []
                                wild_held_items[version].append(item_name)
        
        # Egg groups
        egg_groups = [group.get("name", "") for group in species_data.get("egg_groups", []) 
                     if isinstance(group, dict) and group.get("name")]
        
        # Evolution chain
        evolution_chain = []
        evolution_chain_url = species_data.get("evolution_chain", {}).get("url", "")
        if evolution_chain_url:
            try:
                # Extract ID from URL
                chain_id = evolution_chain_url.rstrip("/").split("/")[-1]
                chain_response = self.client._request("GET", f"/evolution-chain/{chain_id}")
                chain_data = chain_response.json()
                evolution_chain = flatten_evolution_chain(chain_data)
            except Exception:
                pass
        
        # Locations (simplified)
        locations = []
        try:
            encounters_response = self.client._request("GET", f"/pokemon/{species_id}/encounters")
            encounters_data = encounters_response.json()
            for encounter in encounters_data:
                if isinstance(encounter, dict):
                    location_area = encounter.get("location_area", {}).get("name", "")
                    for version_detail in encounter.get("version_details", []):
                        if isinstance(version_detail, dict):
                            version = version_detail.get("version", {}).get("name", "")
                            if location_area and version:
                                locations.append(LocationEntry(version=version, location_area=location_area))
        except Exception:
            pass
        
        # Move learning (simplified - focus on level-up and machine moves)
        pokemon_moves = pokemon_data.get("moves", [])
        level_up_moves_data = filter_moves(pokemon_moves, version_group, "level-up")
        tm_hm_moves_data = filter_moves(pokemon_moves, version_group, "machine")
        tutor_moves_data = filter_moves(pokemon_moves, version_group, "tutor")
        
        # Convert to MoveLearn objects (without detailed move data for now)
        level_up_moves = [
            MoveLearn(
                level=move["level"],
                name=move["name"],
                method=move["method"],
                version_group=move["version_group"]
            ) for move in level_up_moves_data
        ]
        
        tm_hm_moves = [
            MoveLearn(
                level=move["level"],
                name=move["name"],
                method=move["method"],
                version_group=move["version_group"]
            ) for move in tm_hm_moves_data
        ]
        
        tutor_moves = [
            MoveLearn(
                level=move["level"],
                name=move["name"],
                method=move["method"],
                version_group=move["version_group"]
            ) for move in tutor_moves_data
        ]
        
        sprite_url = pick_sprite(pokemon_data, pokedex, sprite_preference)
        
        return PokedexDetailView(
            name=name,
            other_names=other_names,
            national_no=national_no,
            regional_no=regional_no,
            gender_ratio=gender_ratio,
            types=types,
            classification=classification,
            height_m=height_m,
            height_ft_in=height_ft_in,
            weight_kg=weight_kg,
            weight_lbs=weight_lbs,
            capture_rate=capture_rate,
            base_egg_steps=base_egg_steps,
            growth_rate=growth_rate,
            base_happiness=base_happiness,
            ev_yields=ev_yields,
            damage_taken=damage_taken,
            wild_held_items=wild_held_items,
            egg_groups=egg_groups,
            evolution_chain=evolution_chain,
            locations=locations,
            level_up_moves=level_up_moves,
            tm_hm_moves=tm_hm_moves,
            tutor_moves=tutor_moves,
            gen1_only_moves=[],  # TODO: implement gen1-specific logic
            sprite_url=sprite_url
        )


class AsyncPokedexResource:
    """Async Pokedex resource for rankings and detail views."""
    
    def __init__(self, client: AsyncPoke) -> None:
        self.client = client
    
    async def _resolve_generation_to_pokedex(self, generation: int) -> str:
        """Resolve generation number to main region pokedex name."""
        try:
            # Fetch generation data from API
            response = await self.client._request("GET", f"/generation/{generation}")
            generation_data = response.json()
            
            main_region = generation_data.get("main_region")
            if not main_region:
                raise ValueError(f"Generation {generation} has no main region")
            
            region_name = main_region.get("name")
            if not region_name:
                raise ValueError(f"Generation {generation} main region has no name")
            
            # Map region name to appropriate pokedex
            region_to_pokedex = {
                "kanto": "kanto",
                "johto": "original-johto", 
                "hoenn": "hoenn",
                "sinnoh": "sinnoh",  # May not be available
                "unova": "unova",    # May not be available
                "kalos": "central-kalos",  # May not be available
                "alola": "alola",    # May not be available
                "galar": "galar"
            }
            
            pokedex_name = region_to_pokedex.get(region_name)
            if not pokedex_name:
                raise ValueError(f"No pokedex mapping found for region: {region_name}")
            
            return pokedex_name
            
        except Exception as e:
            if "Not Found" in str(e):
                raise ValueError(f"Generation {generation} not found")
            raise ValueError(f"Error resolving generation {generation}: {e}")
    
    async def rankings(
        self,
        *,
        pokedex: Optional[str] = None,
        generation: Optional[int] = None,
        sort_by: str = "total",
        sprite_preference: Optional[str] = None,
        concurrency: int = 6,
    ) -> List[PokedexRankRow]:
        """Get rankings table for a pokedex.
        
        Args:
            pokedex: Pokedex identifier (e.g., "national", "kanto", "original-johto", "hoenn", "galar")
                    Mutually exclusive with generation parameter
            generation: Generation number (1-8) to auto-map to main region pokedex
                       Mutually exclusive with pokedex parameter
            sort_by: Stat to sort by - "total", "hp", "attack", "defense", 
                    "special-attack", "special-defense", "speed"
            sprite_preference: Specific sprite version preference
            concurrency: Number of concurrent requests for async operations
        """
        # Validate parameters
        if pokedex is None and generation is None:
            raise ValueError("Either pokedex or generation parameter must be provided")
        if pokedex is not None and generation is not None:
            raise ValueError("pokedex and generation parameters are mutually exclusive")
        
        # Validate sort_by parameter
        valid_stats = {"total", "hp", "attack", "defense", "special-attack", "special-defense", "speed"}
        if sort_by not in valid_stats:
            raise ValueError(f"sort_by must be one of: {', '.join(valid_stats)}")
        
        # Resolve generation to pokedex if needed
        if generation is not None:
            pokedex = await self._resolve_generation_to_pokedex(generation)
        
        # Fetch the pokedex entries
        response = await self.client._request("GET", f"/pokedex/{pokedex}")
        pokedex_data = response.json()
        
        pokemon_entries = pokedex_data.get("pokemon_entries", [])
        if not pokemon_entries:
            return []
        
        # Use semaphore for controlled concurrency
        semaphore = asyncio.Semaphore(concurrency)
        
        async def fetch_pokemon_data(entry):
            if not isinstance(entry, dict):
                return None
            
            species_name = entry.get("pokemon_species", {}).get("name")
            regional_no = entry.get("entry_number")
            
            if not species_name:
                return None
            
            async with semaphore:
                try:
                    # Fetch pokemon data and species data concurrently
                    pokemon_task = self.client._request("GET", f"/pokemon/{species_name}")
                    species_task = self.client._request("GET", f"/pokemon-species/{species_name}")
                    
                    pokemon_response, species_response = await asyncio.gather(pokemon_task, species_task)
                    
                    pokemon_data = pokemon_response.json()
                    species_data = species_response.json()
                    
                    national_no = species_data.get("id", 0)
                    name = species_data.get("name", species_name)
                    
                    # Build base stats dict
                    base_stats = {}
                    for stat_entry in pokemon_data.get("stats", []):
                        if isinstance(stat_entry, dict):
                            stat_name = stat_entry.get("stat", {}).get("name", "")
                            base_stat = stat_entry.get("base_stat", 0)
                            if stat_name:
                                base_stats[stat_name] = base_stat
                    
                    total_base_stat = calc_total_base_stat(pokemon_data)
                    types = collect_types(pokemon_data)
                    sprite_url = pick_sprite(pokemon_data, pokedex, sprite_preference)
                    
                    return PokedexRankRow(
                        rank=0,  # Will be set after sorting
                        regional_no=regional_no,
                        national_no=national_no,
                        name=name,
                        types=types,
                        base_stats=base_stats,
                        total_base_stat=total_base_stat,
                        sprite_url=sprite_url
                    )
                    
                except Exception:
                    return None
        
        # Fetch all pokemon data concurrently
        tasks = [fetch_pokemon_data(entry) for entry in pokemon_entries]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results and sort by specified stat
        rows = [row for row in results if row is not None]
        
        if sort_by == "total":
            rows.sort(key=lambda x: x.total_base_stat, reverse=True)
        else:
            rows.sort(key=lambda x: x.base_stats.get(sort_by, 0), reverse=True)
        
        # Assign ranks
        for i, row in enumerate(rows):
            row.rank = i + 1
        
        return rows
    
    async def detail(
        self,
        *,
        pokedex: Optional[str] = None,
        generation: Optional[int] = None,
        number: Union[int, str],
        version_group: Optional[str] = None,
        sprite_preference: Optional[str] = None,
        concurrency: int = 6,
    ) -> PokedexDetailView:
        """Get detailed view for a Pokemon."""
        # Validate parameters
        if pokedex is None and generation is None:
            raise ValueError("Either pokedex or generation parameter must be provided")
        if pokedex is not None and generation is not None:
            raise ValueError("pokedex and generation parameters are mutually exclusive")
        
        # Resolve generation to pokedex if needed
        if generation is not None:
            pokedex = await self._resolve_generation_to_pokedex(generation)
        
        # Fetch pokedex entries to resolve number
        pokedex_response = await self.client._request("GET", f"/pokedex/{pokedex}")
        pokedex_data = pokedex_response.json()
        pokemon_entries = pokedex_data.get("pokemon_entries", [])
        
        species_id = resolve_number(pokemon_entries, number)
        
        # Auto-pick version group if not provided
        if version_group is None:
            if pokedex == "kanto":
                version_group = "red-blue"
            elif pokedex == "original-johto":
                version_group = "gold-silver"
            elif pokedex == "updated-johto":
                version_group = "crystal"
            elif pokedex == "hoenn":
                version_group = "ruby-sapphire"
            elif pokedex == "galar":
                version_group = "sword-shield"
            else:
                version_group = "red-blue"  # fallback
        
        # Fetch core data concurrently
        species_task = self.client._request("GET", f"/pokemon-species/{species_id}")
        pokemon_task = self.client._request("GET", f"/pokemon/{species_id}")
        
        species_response, pokemon_response = await asyncio.gather(species_task, pokemon_task)
        
        species_data = species_response.json()
        pokemon_data = pokemon_response.json()
        
        # Basic info
        name = species_data.get("name", "")
        national_no = species_data.get("id", 0)
        regional_no = get_regional_no(species_data, pokedex)
        
        # Names
        other_names = []
        for name_entry in species_data.get("names", []):
            if isinstance(name_entry, dict):
                lang = name_entry.get("language", {}).get("name", "")
                value = name_entry.get("name", "")
                if lang and value and lang != "en":
                    other_names.append(LocalizedName(language=lang, value=value))
        
        # Physical attributes
        height_m = pokemon_data.get("height", 0) / 10.0
        weight_kg = pokemon_data.get("weight", 0) / 10.0
        height_ft_in = ft_in(height_m)
        weight_lbs = kg_to_lbs(weight_kg)
        
        # Species info
        gender_ratio = format_gender_ratio(species_data.get("gender_rate", -1))
        types = collect_types(pokemon_data)
        
        # Find English genus
        classification = None
        for genus_entry in species_data.get("genera", []):
            if isinstance(genus_entry, dict) and genus_entry.get("language", {}).get("name") == "en":
                classification = genus_entry.get("genus", "")
                break
        
        capture_rate = species_data.get("capture_rate", 0)
        base_egg_steps = calc_egg_steps(species_data.get("hatch_counter", 0))
        growth_rate = species_data.get("growth_rate", {}).get("name", "")
        base_happiness = species_data.get("base_happiness", 0)
        
        # EV yields
        ev_yields = []
        for stat_entry in pokemon_data.get("stats", []):
            if isinstance(stat_entry, dict):
                effort = stat_entry.get("effort", 0)
                if effort > 0:
                    stat_name = stat_entry.get("stat", {}).get("name", "")
                    ev_yields.append(EVYield(stat=stat_name, value=effort))
        
        # Type effectiveness - fetch type data concurrently
        type_tasks = [self.client._request("GET", f"/type/{type_name}") for type_name in types]
        type_responses = []
        
        if type_tasks:
            type_responses = await asyncio.gather(*type_tasks, return_exceptions=True)
        
        type_data_cache = {}
        for i, type_name in enumerate(types):
            if i < len(type_responses) and not isinstance(type_responses[i], Exception):
                type_data_cache[type_name] = type_responses[i].json()
            else:
                type_data_cache[type_name] = {}
        
        damage_taken = compute_damage_taken(types, type_data_cache)
        
        # Wild held items
        wild_held_items = {}
        for item_entry in pokemon_data.get("held_items", []):
            if isinstance(item_entry, dict):
                item_name = item_entry.get("item", {}).get("name", "")
                if item_name:
                    for version_detail in item_entry.get("version_details", []):
                        if isinstance(version_detail, dict):
                            version = version_detail.get("version", {}).get("name", "")
                            if version:
                                if version not in wild_held_items:
                                    wild_held_items[version] = []
                                wild_held_items[version].append(item_name)
        
        # Egg groups
        egg_groups = [group.get("name", "") for group in species_data.get("egg_groups", []) 
                     if isinstance(group, dict) and group.get("name")]
        
        # Evolution chain
        evolution_chain = []
        evolution_chain_url = species_data.get("evolution_chain", {}).get("url", "")
        if evolution_chain_url:
            try:
                chain_id = evolution_chain_url.rstrip("/").split("/")[-1]
                chain_response = await self.client._request("GET", f"/evolution-chain/{chain_id}")
                chain_data = chain_response.json()
                evolution_chain = flatten_evolution_chain(chain_data)
            except Exception:
                pass
        
        # Locations
        locations = []
        try:
            encounters_response = await self.client._request("GET", f"/pokemon/{species_id}/encounters")
            encounters_data = encounters_response.json()
            for encounter in encounters_data:
                if isinstance(encounter, dict):
                    location_area = encounter.get("location_area", {}).get("name", "")
                    for version_detail in encounter.get("version_details", []):
                        if isinstance(version_detail, dict):
                            version = version_detail.get("version", {}).get("name", "")
                            if location_area and version:
                                locations.append(LocationEntry(version=version, location_area=location_area))
        except Exception:
            pass
        
        # Move learning
        pokemon_moves = pokemon_data.get("moves", [])
        level_up_moves_data = filter_moves(pokemon_moves, version_group, "level-up")
        tm_hm_moves_data = filter_moves(pokemon_moves, version_group, "machine")
        tutor_moves_data = filter_moves(pokemon_moves, version_group, "tutor")
        
        # Convert to MoveLearn objects
        level_up_moves = [
            MoveLearn(
                level=move["level"],
                name=move["name"],
                method=move["method"],
                version_group=move["version_group"]
            ) for move in level_up_moves_data
        ]
        
        tm_hm_moves = [
            MoveLearn(
                level=move["level"],
                name=move["name"],
                method=move["method"],
                version_group=move["version_group"]
            ) for move in tm_hm_moves_data
        ]
        
        tutor_moves = [
            MoveLearn(
                level=move["level"],
                name=move["name"],
                method=move["method"],
                version_group=move["version_group"]
            ) for move in tutor_moves_data
        ]
        
        sprite_url = pick_sprite(pokemon_data, pokedex, sprite_preference)
        
        return PokedexDetailView(
            name=name,
            other_names=other_names,
            national_no=national_no,
            regional_no=regional_no,
            gender_ratio=gender_ratio,
            types=types,
            classification=classification,
            height_m=height_m,
            height_ft_in=height_ft_in,
            weight_kg=weight_kg,
            weight_lbs=weight_lbs,
            capture_rate=capture_rate,
            base_egg_steps=base_egg_steps,
            growth_rate=growth_rate,
            base_happiness=base_happiness,
            ev_yields=ev_yields,
            damage_taken=damage_taken,
            wild_held_items=wild_held_items,
            egg_groups=egg_groups,
            evolution_chain=evolution_chain,
            locations=locations,
            level_up_moves=level_up_moves,
            tm_hm_moves=tm_hm_moves,
            tutor_moves=tutor_moves,
            gen1_only_moves=[],  # TODO: implement gen1-specific logic
            sprite_url=sprite_url
        )