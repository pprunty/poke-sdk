from __future__ import annotations
import asyncio
import time
import httpx

from ._exceptions import APIConnectionError, APIStatusError, NotFoundError, map_http_error

DEFAULT_BASE_URL = "https://pokeapi.co/api/v2"
DEFAULT_TIMEOUT = 10.0


def _safe_get_response_body(response: httpx.Response) -> str:
    """Safely extract response body for error messages."""
    try:
        # Try to get JSON first (more structured)
        json_data = response.json()
        return str(json_data)
    except Exception:
        # Fallback to text, truncated for safety
        return response.text[:200]


class BaseClient:
    def __init__(
        self,
        *,
        base_url: str | httpx.URL = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        # Defaults kick in here if you don't pass anything
        self._base_url: httpx.URL = httpx.URL(str(base_url).rstrip("/"))
        self._timeout: float = float(timeout)

    @property
    def base_url(self) -> httpx.URL:
        return self._base_url

    @base_url.setter
    def base_url(self, url: str | httpx.URL) -> None:
        self._base_url = httpx.URL(str(url).rstrip("/"))

    @property
    def timeout(self) -> float:
        return self._timeout

    @timeout.setter
    def timeout(self, seconds: float) -> None:
        self._timeout = float(seconds)

    def _join(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return str(self._base_url) + path


class Poke(BaseClient):
    def __init__(
        self,
        *,
        base_url: str | httpx.URL = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        super().__init__(base_url=base_url, timeout=timeout)
        # attach resource namespaces
        from .resources.pokemon import PokemonResource
        from .resources.generation import GenerationResource
        from .resources.search import SearchResource

        self.pokemon = PokemonResource(self)
        self.generation = GenerationResource(self)
        self.search = SearchResource(self)

    def _request(self, method: str, path: str, **kw) -> httpx.Response:
        url = self._join(path)
        timeout = kw.pop("timeout", self._timeout)
        retries = kw.pop("retries", 2)
        backoff = kw.pop("backoff", 0.3)

        for attempt in range(retries + 1):
            try:
                r = httpx.request(method, url, timeout=timeout, **kw)
                if r.status_code >= 500 and attempt < retries:
                    # transient server errors -> retry
                    time.sleep(backoff * (2 ** attempt))
                    continue
                break
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.NetworkError, httpx.HTTPError) as e:
                if attempt < retries:
                    time.sleep(backoff * (2 ** attempt))
                    continue
                raise APIConnectionError(str(e)) from e

        if r.status_code >= 400:
            body = _safe_get_response_body(r)
            raise map_http_error(r.status_code, body)
        return r


class AsyncPoke(BaseClient):
    def __init__(
        self,
        *,
        base_url: str | httpx.URL = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        super().__init__(base_url=base_url, timeout=timeout)
        self._client = httpx.AsyncClient(timeout=self._timeout)
        self._locks: dict[str, asyncio.Lock] = {}
        from .resources.pokemon import AsyncPokemonResource
        from .resources.generation import AsyncGenerationResource
        from .resources.search import AsyncSearchResource

        self.pokemon = AsyncPokemonResource(self)
        self.generation = AsyncGenerationResource(self)
        self.search = AsyncSearchResource(self)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _request(self, method: str, path: str, **kw) -> httpx.Response:
        url = self._join(path)
        timeout = kw.pop("timeout", self._timeout)
        retries = kw.pop("retries", 2)
        backoff = kw.pop("backoff", 0.3)

        # Update the async client timeout if needed
        if timeout != self._timeout:
            kw["timeout"] = timeout

        for attempt in range(retries + 1):
            try:
                r = await self._client.request(method, url, **kw)
                if r.status_code >= 500 and attempt < retries:
                    # transient server errors -> retry
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                break
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.NetworkError, httpx.HTTPError) as e:
                if attempt < retries:
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                raise APIConnectionError(str(e)) from e

        if r.status_code >= 400:
            body = _safe_get_response_body(r)
            raise map_http_error(r.status_code, body)
        return r
