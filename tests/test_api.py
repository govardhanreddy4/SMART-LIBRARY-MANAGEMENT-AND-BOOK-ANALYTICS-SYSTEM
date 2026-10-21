"""Unit tests for Google Books REST API integration with mocked HTTP responses."""

import pytest
from unittest.mock import patch, MagicMock
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api.google_books import GoogleBooksAPI, BookAPIError


class TestGoogleBooksAPI:
    """Test suite verifying REST API query formatting, response parsing, and error conditions."""

    @pytest.fixture
    def mock_volume_response(self):
        return {
            "items": [
                {
                    "id": "abc1234",
                    "volumeInfo": {
                        "title": "Design Patterns",
                        "authors": ["Erich Gamma", "Richard Helm"],
                        "publisher": "Addison-Wesley",
                        "publishedDate": "1994-10-21",
                        "description": "Elements of Reusable Object-Oriented Software",
                        "industryIdentifiers": [
                            {"type": "ISBN_13", "identifier": "9780201633610"}
                        ],
                        "categories": ["Computers"],
                        "imageLinks": {
                            "thumbnail": "http://books.google.com/books/content?id=abc&zoom=1"
                        },
                        "pageCount": 395
                    }
                }
            ]
        }

    @patch("requests.get")
    def test_search_books_success(self, mock_get, mock_volume_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_volume_response
        mock_get.return_value = mock_response

        api = GoogleBooksAPI()
        results = api.search_books("Design Patterns")

        assert len(results) == 1
        book = results[0]
        assert book["title"] == "Design Patterns"
        assert "Erich Gamma" in book["author"]
        assert book["isbn"] == "9780201633610"
        assert book["thumbnail_url"].startswith("https://")  # Converted to https
        assert book["suggested_book_id"] == "GB-9780201633610"

    @patch("requests.get")
    def test_search_books_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        api = GoogleBooksAPI()
        with pytest.raises(BookAPIError) as exc:
            api.search_books("Query")
        assert "timed out" in str(exc.value).lower()

    @patch("requests.get")
    def test_search_books_rate_limit(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        api = GoogleBooksAPI()
        with pytest.raises(BookAPIError) as exc:
            api.search_books("Query")
        assert "rate limit" in str(exc.value).lower()

    @patch("requests.get")
    def test_search_books_missing_fields(self, mock_get):
        """Verify incomplete API item does not crash parser."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "bare_item_001",
                    "volumeInfo": {}  # Empty volumeInfo
                }
            ]
        }
        mock_get.return_value = mock_response

        api = GoogleBooksAPI()
        results = api.search_books("Bare")
        assert len(results) == 1
        assert results[0]["title"] == "Unknown Title"
        assert results[0]["author"] == "Unknown Author"
        assert results[0]["isbn"] == ""
