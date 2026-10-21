"""AsyncIO tasks demonstration for concurrent external data enrichment."""

import asyncio
from typing import List, Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api.google_books import GoogleBooksAPI
from utils.logging_config import get_logger

logger = get_logger("concurrency.async_tasks")


class AsyncTaskManager:
    """Orchestrates AsyncIO workloads for concurrent network operations.
    
    Demonstrates:
    - Module III: AsyncIO coroutines and event loop execution
    - asyncio.gather() for concurrent HTTP queries
    - Bridge between synchronous GUI code and asynchronous coroutines
    """

    def __init__(self):
        self.api = GoogleBooksAPI()

    async def fetch_multiple_categories_async(self, categories: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Asynchronously fetch books across multiple categories concurrently."""
        logger.info("Starting concurrent async fetch for %d categories...", len(categories))
        return await self.api.search_multiple_queries_async(categories)

    def run_concurrent_search(self, search_terms: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Synchronous wrapper to execute the asyncio event loop safely."""
        try:
            return asyncio.run(self.fetch_multiple_categories_async(search_terms))
        except RuntimeError:
            # Handle case where an event loop is already running (e.g., inside Jupyter or asyncio thread)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.fetch_multiple_categories_async(search_terms))
            finally:
                loop.close()
