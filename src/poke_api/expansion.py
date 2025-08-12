# src/poke_api/expansion.py
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional
import asyncio
import copy

# --- Helpers ---------------------------------------------------------------


def _model_to_dict(obj: Any) -> Dict[str, Any]:
    """Supports Pydantic v2 models; falls back to dict-like. Always returns a deep copy."""
    if hasattr(obj, "to_dict"):
        result = obj.to_dict()
    elif hasattr(obj, "model_dump"):
        result = obj.model_dump(exclude_none=True)  # pydantic v2
    elif isinstance(obj, dict):
        result = obj
    else:
        # Final fallback – best-effort:
        result = dict(obj)

    # Always return a deep copy to avoid mutating the original
    return copy.deepcopy(result)


def _is_ref_like(v: Any) -> bool:
    """PokéAPI refs are APIResource {url} or NamedAPIResource {name,url}"""
    return isinstance(v, dict) and isinstance(v.get("url"), str)


def _flatten(xs: Iterable[Any]) -> List[Any]:
    out: List[Any] = []
    for x in xs:
        if isinstance(x, list):
            out.extend(x)
        else:
            out.append(x)
    return out


def _get_at_path(root: Dict[str, Any], path: str) -> List[Dict[str, Any]]:
    """
    Dot-path extractor that tolerates arrays: e.g. "moves.move" finds all dicts under:
    root["moves"][*]["move"].
    Returns a list of dict nodes (not copies).
    """
    segs = path.split(".")
    frontier: List[Any] = [root]
    for seg in segs:
        nxt: List[Any] = []
        for node in frontier:
            if isinstance(node, list):
                for item in node:
                    if isinstance(item, dict) and seg in item:
                        nxt.append(item[seg])
            elif isinstance(node, dict) and seg in node:
                nxt.append(node[seg])
        frontier = _flatten(nxt)
    # keep only dicts (refs will be dicts with {"url": ...})
    return [n for n in frontier if isinstance(n, dict)]


def _collect_immediate_refs(node: Any) -> List[Dict[str, Any]]:
    """Find direct children that are ref-like (including inside lists)."""
    out: List[Dict[str, Any]] = []
    if isinstance(node, dict):
        for v in node.values():
            if _is_ref_like(v):
                out.append(v)
            elif isinstance(v, list):
                for it in v:
                    if _is_ref_like(it):
                        out.append(it)
    return out


# --- SYNC expansion --------------------------------------------------------


def expand_sync(
    client,  # Poke
    obj: Any,
    *,
    paths: Optional[List[str]] = None,
    depth: int = 1,
    max_requests: int = 200,
) -> Dict[str, Any]:
    """
    Returns a dict copy of `obj` with expansions attached under '__expanded__' on each ref.
    Does not mutate the original model.
    """
    root = _model_to_dict(obj)
    seen: set[str] = set()
    budget = max_requests

    # Seed queue with refs from selected paths or from root (1-level only).
    queue: List[Dict[str, Any]] = []
    if paths:
        for p in paths:
            for node in _get_at_path(root, p):
                if _is_ref_like(node):
                    queue.append(node)
    else:
        queue.extend(_collect_immediate_refs(root))

    # Cache fetched data to avoid duplicate requests
    url_data_cache = {}

    for _ in range(max(0, depth)):
        if not queue or budget <= 0:
            break
        current, queue = queue, []
        for ref in current:
            url = ref.get("url")
            if not url:
                continue

            # If we've already fetched this URL, use cached data
            if url in url_data_cache:
                ref["__expanded__"] = url_data_cache[url]
                # Add refs from cached data for next depth
                queue.extend(_collect_immediate_refs(url_data_cache[url]))
            elif url not in seen and budget > 0:
                # Fetch new URL
                seen.add(url)
                budget -= 1
                data = client._get_json_by_url(url)
                # Cache the data
                url_data_cache[url] = data
                # Attach fetched data under a reserved key:
                ref["__expanded__"] = data
                # For next depth, collect refs inside the fetched payload
                queue.extend(_collect_immediate_refs(data))
    return root


# --- ASYNC expansion -------------------------------------------------------


async def expand_async(
    client,  # AsyncPoke
    obj: Any,
    *,
    paths: Optional[List[str]] = None,
    depth: int = 1,
    max_requests: int = 200,
    concurrency: int = 6,
) -> Dict[str, Any]:
    """
    Async variant with bounded concurrency. Returns a dict copy (original model untouched).
    """
    root = _model_to_dict(obj)
    seen: set[str] = set()
    budget = max_requests
    sem = asyncio.Semaphore(max(1, concurrency))

    # Cache fetched data to avoid duplicate requests
    url_data_cache = {}

    async def fetch_and_attach(ref: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        nonlocal budget
        url = ref.get("url")
        if not url:
            return None

        # If already cached, use cached data
        if url in url_data_cache:
            ref["__expanded__"] = url_data_cache[url]
            return _collect_immediate_refs(url_data_cache[url])

        # If not seen and budget available, fetch it
        if url not in seen and budget > 0:
            seen.add(url)
            budget -= 1
            async with sem:
                data = await client._aget_json_by_url(url)
            url_data_cache[url] = data
            ref["__expanded__"] = data
            return _collect_immediate_refs(data)
        return None

    # Seed queue
    queue: List[Dict[str, Any]] = []
    if paths:
        for p in paths:
            for node in _get_at_path(root, p):
                if _is_ref_like(node):
                    queue.append(node)
    else:
        queue.extend(_collect_immediate_refs(root))

    for _ in range(max(0, depth)):
        if not queue or budget <= 0:
            break
        current, queue = queue, []
        tasks = [fetch_and_attach(ref) for ref in current]
        results = await asyncio.gather(*tasks)
        # Add next-level refs
        for r in results:
            if r:
                queue.extend(r)

    return root
