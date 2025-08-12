"""Stainless-style pagination support for PokeAPI."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar
from urllib.parse import parse_qs, urlparse

if TYPE_CHECKING:
    pass

T = TypeVar("T")


class _PageBase(Generic[T]):
    """Base class for paginated results with navigation methods."""

    def __init__(
        self,
        *,
        result: Sequence[T],
        count: int,
        next: Optional[str],
        previous: Optional[str],
        client,
        endpoint: str,
        original_params: dict[str, Any],
    ):
        self.result = list(result)
        self.count = count
        self.next = next
        self.previous = previous
        self._client = client
        self._endpoint = endpoint
        self._original_params = dict(original_params)

    def has_next_page(self) -> bool:
        """Check if there is a next page available."""
        return bool(self.next)

    def has_previous_page(self) -> bool:
        """Check if there is a previous page available."""
        return bool(self.previous)

    def next_page_info(self) -> Optional[dict[str, Any]]:
        """Parse the next URL to extract pagination parameters."""
        if not self.next:
            return None

        parsed = urlparse(self.next)
        query_params = parse_qs(parsed.query)

        # Flatten single values and convert numeric strings to integers
        info: dict[str, Any] = {}
        for key, values in query_params.items():
            if values:
                value = values[0]
                # Try to convert to int if it looks like a number
                if value.isdigit():
                    info[key] = int(value)
                else:
                    info[key] = value

        return info

    def previous_page_info(self) -> Optional[dict[str, Any]]:
        """Parse the previous URL to extract pagination parameters."""
        if not self.previous:
            return None

        parsed = urlparse(self.previous)
        query_params = parse_qs(parsed.query)

        # Flatten single values and convert numeric strings to integers
        info: dict[str, Any] = {}
        for key, values in query_params.items():
            if values:
                value = values[0]
                # Try to convert to int if it looks like a number
                if value.isdigit():
                    info[key] = int(value)
                else:
                    info[key] = value

        return info

    def __repr__(self) -> str:
        """Friendly representation of the page."""
        class_name = self.__class__.__name__
        return f"{class_name}(result={len(self.result)} items, count={self.count}, has_next={self.has_next_page()})"


class Page(_PageBase[T]):
    """Synchronous paginated result with navigation methods."""

    def get_next_page(self) -> Page[T]:
        """Fetch the next page using the same resource."""
        info = self.next_page_info()
        if not info:
            raise StopIteration("No next page available")

        # Use the client's internal helper method
        return self._client._list(self._endpoint, **info)

    def get_previous_page(self) -> Page[T]:
        """Fetch the previous page using the same resource."""
        info = self.previous_page_info()
        if not info:
            raise StopIteration("No previous page available")

        # Use the client's internal helper method
        return self._client._list(self._endpoint, **info)

    def __iter__(self):
        """Enable auto-pagination iteration over all pages."""
        current_page = self
        while True:
            # Yield all items from current page
            for item in current_page.result:
                yield item

            # Check if there's a next page
            if not current_page.has_next_page():
                break

            # Fetch next page and continue iteration
            current_page = current_page.get_next_page()


class AsyncPage(_PageBase[T]):
    """Asynchronous paginated result with navigation methods."""

    async def get_next_page(self) -> AsyncPage[T]:
        """Fetch the next page using the same resource."""
        info = self.next_page_info()
        if not info:
            raise StopIteration("No next page available")

        # Use the client's internal helper method
        return await self._client._alist(self._endpoint, **info)

    async def get_previous_page(self) -> AsyncPage[T]:
        """Fetch the previous page using the same resource."""
        info = self.previous_page_info()
        if not info:
            raise StopIteration("No previous page available")

        # Use the client's internal helper method
        return await self._client._alist(self._endpoint, **info)

    def __aiter__(self):
        """Enable async auto-pagination iteration over all pages."""
        self._current_page = self
        self._current_index = 0
        return self

    async def __anext__(self):
        """Get next item, automatically fetching new pages as needed."""
        # If we have more items in current page, return next item
        if self._current_index < len(self._current_page.result):
            item = self._current_page.result[self._current_index]
            self._current_index += 1
            return item

        # Current page is exhausted, try to get next page
        if not self._current_page.has_next_page():
            raise StopAsyncIteration

        # Fetch next page and reset index
        self._current_page = await self._current_page.get_next_page()
        self._current_index = 0

        # Return first item from new page
        if self._current_page.result:
            item = self._current_page.result[self._current_index]
            self._current_index += 1
            return item
        else:
            # Empty page, stop iteration
            raise StopAsyncIteration
