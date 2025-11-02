"""HTTP client utilities with caching and retry logic."""

from hishel.httpx import AsyncCacheClient
from .yfinance_helpers import api_retry

# Minimal HTTP Headers - only essential ones
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def create_async_client(headers: dict | None = None) -> AsyncCacheClient:
    """Create a cached async HTTP client with longer timeout, automatic redirect and custom headers.
    
    Args:
        headers: Optional custom headers to include in requests
        
    Returns:
        Configured AsyncCacheClient instance
    """
    return AsyncCacheClient(
        timeout=30.0,
        follow_redirects=True,
        headers=headers,
    )


@api_retry
async def fetch_json(url: str, headers: dict | None = None) -> dict:
    """Generic JSON fetcher with retry logic.
    
    Args:
        url: URL to fetch JSON from
        headers: Optional custom headers
        
    Returns:
        Parsed JSON response as dictionary
        
    Raises:
        httpx.HTTPStatusError: If response status is not successful
    """
    async with create_async_client(headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@api_retry
async def fetch_text(url: str, headers: dict | None = None) -> str:
    """Generic text fetcher with retry logic.
    
    Args:
        url: URL to fetch text from
        headers: Optional custom headers
        
    Returns:
        Response text content
        
    Raises:
        httpx.HTTPStatusError: If response status is not successful
    """
    async with create_async_client(headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
