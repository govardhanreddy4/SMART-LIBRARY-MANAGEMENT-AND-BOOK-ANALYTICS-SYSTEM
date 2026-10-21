"""Unit tests for Book Model, BookService, and Module I/II Advanced Concepts."""

import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.schema import init_db
from database.repositories import BookRepository
from models.book import Book
from services.book_service import BookService, CatalogIterator


class TestBooks:
    """Test suite for Book entity, repository, service, and functional programming features."""

    @pytest.fixture
    def book_service(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_path = f.name
        init_db(temp_path, seed_samples=False)
        repo = BookRepository(temp_path)
        service = BookService(repo)
        yield service
        try:
            Path(temp_path).unlink(missing_ok=True)
        except Exception:
            pass

    def test_book_model_encapsulation_and_operators(self):
        """Demonstrates testing Operator Overloading (<, +, ==) and Encapsulation."""
        b1 = Book("B1", "Algorithms", "Cormen", "CS", 1000.0, 5, 2)
        b2 = Book("B2", "Basic Python", "Author", "CS", 400.0, 5, 4)

        # Operator Overloading `<` (comparing available copies)
        assert b1 < b2  # 2 < 4
        assert not (b2 < b1)

        # Operator Overloading `+` (adding stock copies)
        b1 + 3
        assert b1.total_copies == 8
        assert b1.available_copies == 5

        # Dunder `__len__`
        assert len(b1) == 5

        # Invariant: available cannot exceed total
        with pytest.raises(ValueError):
            b1.available_copies = 100

        # Invariant: price cannot be negative
        with pytest.raises(ValueError):
            b1.price = -50.0

    def test_book_crud_lifecycle(self, book_service):
        # Create
        book = book_service.add_book(
            book_id="BK-TEST-1",
            title="Clean Architecture",
            author="Robert C. Martin",
            category="Software Engineering",
            price=750.0,
            total_copies=4,
            available_copies=4
        )
        assert book.book_id == "BK-TEST-1"

        # Read
        retrieved = book_service.get_book("BK-TEST-1")
        assert retrieved is not None
        assert retrieved.title == "Clean Architecture"

        # Update
        updated = book_service.update_book(
            book_id="BK-TEST-1",
            title="Clean Architecture (2nd Edition)",
            author="Robert C. Martin",
            category="Software Engineering",
            price=800.0,
            total_copies=5,
            available_copies=5
        )
        assert updated.price == 800.0
        assert updated.total_copies == 5

        # Delete
        success = book_service.delete_book("BK-TEST-1")
        assert success is True
        assert book_service.get_book("BK-TEST-1") is None

    def test_functional_programming_demonstrations(self, book_service):
        """Verify lambda, map, filter, reduce, and comprehensions."""
        book_service.add_book("B1", "Book One", "Author A", "Science", 100.0, 3, 0)  # out of stock
        book_service.add_book("B2", "Book Two", "Author B", "Science", 200.0, 4, 3)  # in stock
        book_service.add_book("B3", "Book Three", "Author C", "Arts", 300.0, 2, 2)   # in stock

        # filter() with lambda
        avail = book_service.filter_available_books()
        assert len(avail) == 2
        assert {b.book_id for b in avail} == {"B2", "B3"}

        # map() with lambda
        summaries = book_service.format_book_summaries()
        assert len(summaries) == 3
        assert any("[B1]" in s for s in summaries)

        # functools.reduce() with lambda
        # Total val = (100*3) + (200*4) + (300*2) = 300 + 800 + 600 = 1700.0
        val = book_service.calculate_total_inventory_valuation()
        assert val == 1700.0

        # Set comprehension
        cats = book_service.get_distinct_categories_set_comp()
        assert cats == {"Science", "Arts"}

        # Dictionary comprehension
        lookup = book_service.get_stock_lookup_dict_comp()
        assert lookup == {"B1": 0, "B2": 3, "B3": 2}

        # List comprehension
        low_stock = book_service.get_low_stock_titles_list_comp(threshold=1)
        assert "Book One" in low_stock

    def test_generator_and_iterator(self, book_service):
        for i in range(1, 11):
            book_service.add_book(f"BK-{i}", f"Title {i}", "Author", "Cat", 100.0, 2, 2)

        # Generator test
        batches = list(book_service.stream_books_generator(batch_size=4))
        assert len(batches) == 3
        assert len(batches[0]) == 4
        assert len(batches[1]) == 4
        assert len(batches[2]) == 2

        # Iterator test
        it = book_service.get_catalog_iterator()
        assert isinstance(it, CatalogIterator)
        first_book = next(it)
        assert isinstance(first_book, Book)
