"""Book Service demonstrating Functional Programming, Iterators, Generators, and CRUD operations."""

from functools import reduce
from typing import List, Dict, Any, Optional, Iterator, Generator, Callable
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.repositories import BookRepository
from models.book import Book
from utils.validators import Validators
from utils.file_handlers import DataExporter, DataImporter
from utils.logging_config import get_logger

logger = get_logger("services.book_service")


# Module II: Custom Iterator (Iterable Object)
class CatalogIterator:
    """Custom Iterator demonstrating `__iter__` and `__next__` protocols for Book collections.
    
    Demonstrates:
    - Module II: An iterator / iterable object
    """

    def __init__(self, books: List[Book]):
        self._books = books
        self._index = 0

    def __iter__(self) -> "CatalogIterator":
        return self

    def __next__(self) -> Book:
        if self._index < len(self._books):
            book = self._books[self._index]
            self._index += 1
            return book
        raise StopIteration


class BookService:
    """Service handling book lifecycle and catalog analytics.
    
    Demonstrates:
    - Module II: Lambda expressions
    - Module II: map() and filter()
    - Module II: functools.reduce()
    - Module II: List, Set, and Dictionary comprehensions
    - Module II: Generator function
    - Module II: Custom Iterator
    - Module II: Higher-Order Function
    """

    def __init__(self, book_repo: Optional[BookRepository] = None):
        self.repo = book_repo or BookRepository()

    # --- Core CRUD Operations ---

    def add_book(
        self,
        book_id: str,
        title: str,
        author: str,
        category: str,
        price: float,
        total_copies: int,
        available_copies: Optional[int] = None
    ) -> Book:
        """Validate and insert a new book record."""
        ok, err = Validators.validate_book_inputs(
            book_id, title, author, category, price, total_copies, available_copies
        )
        if not ok:
            raise ValueError(err)

        avail = total_copies if available_copies is None else available_copies
        book = Book(
            book_id=book_id,
            title=title,
            author=author,
            category=category,
            price=price,
            total_copies=total_copies,
            available_copies=avail
        )
        self.repo.add_book(book)
        return book

    def get_book(self, book_id: str) -> Optional[Book]:
        """Fetch book by ID."""
        return self.repo.get_book_by_id(book_id)

    def get_all_books(self) -> List[Book]:
        """Fetch all books."""
        return self.repo.get_all_books()

    def update_book(
        self,
        book_id: str,
        title: str,
        author: str,
        category: str,
        price: float,
        total_copies: int,
        available_copies: int
    ) -> Book:
        """Validate and update book record."""
        ok, err = Validators.validate_book_inputs(
            book_id, title, author, category, price, total_copies, available_copies
        )
        if not ok:
            raise ValueError(err)

        existing = self.repo.get_book_by_id(book_id)
        if not existing:
            raise ValueError(f"Book '{book_id}' does not exist.")

        book = Book(
            book_id=book_id,
            title=title,
            author=author,
            category=category,
            price=price,
            total_copies=total_copies,
            available_copies=available_copies
        )
        self.repo.update_book(book)
        return book

    def delete_book(self, book_id: str) -> bool:
        """Delete book safely (enforcing loan history retention)."""
        return self.repo.delete_book(book_id)

    def search_books(self, query: str = "", category: str = "") -> List[Book]:
        """Search books with filtering."""
        return self.repo.search_books(query, category)

    def get_categories(self) -> List[str]:
        """Get list of distinct categories."""
        return self.repo.get_categories()

    # --- Module II: Functional Programming Demonstrations ---

    def filter_available_books(self, books: Optional[List[Book]] = None) -> List[Book]:
        """Demonstrates `filter()` and `lambda` to filter books currently on shelves."""
        catalog = books if books is not None else self.get_all_books()
        # Module II: filter() with lambda
        return list(filter(lambda b: b.is_available, catalog))

    def format_book_summaries(self, books: Optional[List[Book]] = None) -> List[str]:
        """Demonstrates `map()` and `lambda` to transform book objects to formatted summaries."""
        catalog = books if books is not None else self.get_all_books()
        # Module II: map() with lambda
        return list(map(lambda b: f"[{b.book_id}] {b.title} ({b.author}) - ₹{b.price:.2f}", catalog))

    def calculate_total_inventory_valuation(self, books: Optional[List[Book]] = None) -> float:
        """Demonstrates `functools.reduce()` with lambda to compute total inventory value."""
        catalog = books if books is not None else self.get_all_books()
        if not catalog:
            return 0.0
        # Module II: functools.reduce() accumulating (price * total_copies)
        total_val = reduce(lambda acc, b: acc + (b.price * b.total_copies), catalog, 0.0)
        return round(total_val, 2)

    def get_distinct_categories_set_comp(self, books: Optional[List[Book]] = None) -> set[str]:
        """Demonstrates Set Comprehension to extract unique categories."""
        catalog = books if books is not None else self.get_all_books()
        # Module II: Set comprehension
        return {b.category for b in catalog}

    def get_stock_lookup_dict_comp(self, books: Optional[List[Book]] = None) -> Dict[str, int]:
        """Demonstrates Dictionary Comprehension mapping book_id to available_copies."""
        catalog = books if books is not None else self.get_all_books()
        # Module II: Dictionary comprehension
        return {b.book_id: b.available_copies for b in catalog}

    def get_low_stock_titles_list_comp(self, threshold: int = 2) -> List[str]:
        """Demonstrates List Comprehension filtering titles with low remaining copies."""
        catalog = self.get_all_books()
        # Module II: List comprehension with conditional filtering
        return [b.title for b in catalog if b.available_copies <= threshold]

    # --- Module II: Generator Function ---

    def stream_books_generator(self, batch_size: int = 5) -> Generator[List[Book], None, None]:
        """Generator function streaming books in batches to conserve memory.
        
        Demonstrates:
        - Module II: Python Generator using `yield`
        """
        all_books = self.get_all_books()
        for i in range(0, len(all_books), batch_size):
            yield all_books[i:i + batch_size]

    def get_catalog_iterator(self) -> CatalogIterator:
        """Return custom iterator over all books."""
        return CatalogIterator(self.get_all_books())

    # --- Module II: Higher-Order Function ---

    def filter_by_custom_predicate(self, predicate: Callable[[Book], bool]) -> List[Book]:
        """Higher-Order function accepting a custom filtering predicate function.
        
        Demonstrates:
        - Module II: Higher-order function receiving a Callable
        """
        return [b for b in self.get_all_books() if predicate(b)]

    # --- Import / Export Handlers ---

    def export_catalog(self, file_path: str, format_type: str = "CSV") -> bool:
        """Export book catalog to CSV, JSON, or XML."""
        books = [b.to_dict() for b in self.get_all_books()]
        fmt = format_type.upper()
        if fmt == "CSV":
            return DataExporter.export_to_csv(books, file_path)
        elif fmt == "JSON":
            return DataExporter.export_to_json(books, file_path)
        elif fmt == "XML":
            return DataExporter.export_to_xml(books, file_path, "catalog", "book")
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def import_catalog(self, file_path: str, format_type: str = "CSV") -> Dict[str, Any]:
        """Import books from CSV or JSON with validation and collision handling."""
        fmt = format_type.upper()
        if fmt == "CSV":
            records, errors = DataImporter.import_from_csv(file_path)
        elif fmt == "JSON":
            records, errors = DataImporter.import_from_json(file_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        imported_count = 0
        skipped_count = 0
        for rec in records:
            existing = self.repo.get_book_by_id(rec["book_id"])
            if existing:
                skipped_count += 1
                errors.append(f"Skipped existing book ID: {rec['book_id']}")
                continue
            
            try:
                self.add_book(**rec)
                imported_count += 1
            except Exception as e:
                errors.append(f"Failed to add '{rec['book_id']}': {e}")
                skipped_count += 1

        return {
            "imported": imported_count,
            "skipped": skipped_count,
            "errors": errors
        }
