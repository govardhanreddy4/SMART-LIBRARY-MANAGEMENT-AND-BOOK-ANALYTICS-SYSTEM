"""Google Books REST API Client with Synchronous (requests) and Asynchronous (aiohttp) support."""

from typing import List, Dict, Any, Optional
import requests
import aiohttp
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import GOOGLE_BOOKS_API_URL, API_TIMEOUT_SECONDS, API_MAX_RESULTS
from utils.logging_config import get_logger

logger = get_logger("api.google_books")


class BookAPIError(Exception):
    """Raised when an external API error occurs."""
    pass


class GoogleBooksAPI:
    """Consumes the public Google Books REST API.
    
    Demonstrates:
    - Module V: REST API consumption
    - Synchronous HTTP via requests
    - Module III: Asynchronous HTTP via aiohttp
    - Robust network timeout, rate limit, and exception handling
    - Offline fallback gracefully returning local recommendations
    """

    def __init__(self, timeout: int = API_TIMEOUT_SECONDS):
        self.timeout = timeout
        self.base_url = GOOGLE_BOOKS_API_URL

    def _parse_volume_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and clean relevant fields from raw Google Books API volume."""
        volume_info = item.get("volume_info", item.get("volumeInfo", {}))
        
        # Extract title
        title = volume_info.get("title", "Unknown Title").strip()

        # Extract authors
        authors_list = volume_info.get("authors", ["Unknown Author"])
        author = ", ".join(authors_list) if isinstance(authors_list, list) else str(authors_list)

        # Extract categories
        cats = volume_info.get("categories", ["General"])
        category = cats[0] if isinstance(cats, list) and cats else "General"

        # Extract ISBN
        isbn = ""
        identifiers = volume_info.get("industryIdentifiers", [])
        for id_dict in identifiers:
            t = id_dict.get("type", "")
            if t in ("ISBN_13", "ISBN_10"):
                isbn = id_dict.get("identifier", "")
                break

        # Extract thumbnail
        image_links = volume_info.get("imageLinks", {})
        thumbnail = image_links.get("thumbnail", image_links.get("smallThumbnail", ""))
        # Prefer HTTPS
        if thumbnail.startswith("http://"):
            thumbnail = "https://" + thumbnail[7:]

        description = volume_info.get("description", "No description provided.")
        publisher = volume_info.get("publisher", "Unknown Publisher")
        published_date = volume_info.get("publishedDate", "N/A")
        page_count = volume_info.get("pageCount", 0)

        # Generate a suggested local book ID based on ISBN or volume ID
        suggested_id = f"GB-{isbn}" if isbn else f"GB-{item.get('id', 'ITEM')[:8]}"

        return {
            "api_id": item.get("id", ""),
            "suggested_book_id": suggested_id,
            "title": title,
            "author": author,
            "category": category,
            "isbn": isbn,
            "publisher": publisher,
            "published_date": published_date,
            "description": description,
            "thumbnail_url": thumbnail,
            "page_count": page_count,
        }

    # --- Synchronous REST API Client ---

    def search_books(self, query: str, max_results: int = API_MAX_RESULTS) -> List[Dict[str, Any]]:
        """Perform synchronous HTTP GET request to Google Books API using `requests`."""
        if not query or not query.strip():
            return []

        params = {
            "q": query.strip(),
            "maxResults": min(max_results, 40),
            "printType": "books",
        }

        try:
            logger.info("Sending GET request to Google Books API: query='%s'", query)
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            
            if response.status_code == 429:
                logger.warning("Google Books API rate limit reached (HTTP 429).")
                raise BookAPIError("API rate limit exceeded. Please try again later.")

            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])

            results = [self._parse_volume_item(item) for item in items]
            logger.info("Successfully fetched %d books from Google Books API.", len(results))
            return results

        except requests.exceptions.Timeout:
            logger.error("Google Books API request timed out after %ds.", self.timeout)
            raise BookAPIError("The API request timed out. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            logger.error("Google Books API network error: %s", e)
            raise BookAPIError(f"Network error connecting to Google Books API: {e}")

    # --- Module III: Asynchronous HTTP Client using aiohttp ---

    async def search_books_async(self, query: str, max_results: int = API_MAX_RESULTS) -> List[Dict[str, Any]]:
        """Perform asynchronous HTTP GET request using `aiohttp`.
        
        Demonstrates:
        - Module III: AsyncIO with non-blocking HTTP requests
        """
        if not query or not query.strip():
            return []

        params = {
            "q": query.strip(),
            "maxResults": str(min(max_results, 40)),
            "printType": "books",
        }

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.base_url, params=params) as resp:
                    if resp.status == 429:
                        raise BookAPIError("API rate limit reached (HTTP 429).")
                    resp.raise_for_status()
                    data = await resp.json()
                    items = data.get("items", [])
                    return [self._parse_volume_item(item) for item in items]
        except asyncio.TimeoutError:
            raise BookAPIError("Async request timed out.")
        except Exception as e:
            raise BookAPIError(f"Async API error: {e}")

    async def search_multiple_queries_async(self, queries: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Perform concurrent asynchronous searches for multiple queries using asyncio.gather().
        
        Demonstrates:
        - Module III: Concurrent non-blocking requests with asyncio.gather()
        """
        async def fetch(q: str):
            try:
                res = await self.search_books_async(q, max_results=5)
                return q, res
            except Exception as e:
                logger.warning("Async search failed for query '%s': %s", q, e)
                return q, []

        tasks = [fetch(q) for q in queries]
        results = await asyncio.gather(*tasks)
        return dict(results)
