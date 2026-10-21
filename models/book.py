"""Book model demonstrating Operator Overloading, Encapsulation, and Class Methods."""

from typing import Dict, Any, Union


class Book:
    """Represents a catalogued book in the library system.
    
    Demonstrates:
    - Module I: Classes and objects, constructors and initialization
    - Module I: Encapsulation (protected fields with boundary-checking @property setters)
    - Module I: Operator Overloading:
        * `<` (__lt__): comparing book price or available inventory for sorting
        * `+` (__add__): adding stock copies to book
        * `==` (__eq__): checking book identity by unique book_id
    - Module I: Special/dunder methods (__repr__, __str__, __len__)
    - Module I: Class method (from_row, from_dict)
    """

    def __init__(
        self,
        book_id: str,
        title: str,
        author: str,
        category: str,
        price: float,
        total_copies: int,
        available_copies: int = None
    ):
        self.book_id = str(book_id).strip()
        self.title = str(title).strip()
        self.author = str(author).strip()
        self.category = str(category).strip()
        
        self._price = 0.0
        self._total_copies = 1
        self._available_copies = 1

        self.price = price
        self.total_copies = total_copies
        self.available_copies = total_copies if available_copies is None else available_copies

    # Encapsulation: Price
    @property
    def price(self) -> float:
        """Get book price."""
        return self._price

    @price.setter
    def price(self, val: float) -> None:
        """Set book price with non-negativity constraint."""
        val_f = float(val)
        if val_f < 0.0:
            raise ValueError(f"Book price cannot be negative: {val_f}")
        self._price = round(val_f, 2)

    # Encapsulation: Total Copies
    @property
    def total_copies(self) -> int:
        """Get total physical copies."""
        return self._total_copies

    @total_copies.setter
    def total_copies(self, val: int) -> None:
        """Set total physical copies (must be >= 1)."""
        val_i = int(val)
        if val_i <= 0:
            raise ValueError(f"Total copies must be at least 1: {val_i}")
        self._total_copies = val_i

    # Encapsulation: Available Copies with boundary invariant
    @property
    def available_copies(self) -> int:
        """Get available physical copies."""
        return self._available_copies

    @available_copies.setter
    def available_copies(self, val: int) -> None:
        """Set available copies maintaining invariant: 0 <= available <= total."""
        val_i = int(val)
        if val_i < 0:
            raise ValueError(f"Available copies cannot be negative: {val_i}")
        if val_i > self._total_copies:
            raise ValueError(
                f"Available copies ({val_i}) cannot exceed total copies ({self._total_copies})"
            )
        self._available_copies = val_i

    @property
    def is_available(self) -> bool:
        """Check if at least one copy is on shelf."""
        return self._available_copies > 0

    @property
    def issued_copies(self) -> int:
        """Count currently loaned copies."""
        return self._total_copies - self._available_copies

    # Inventory mutation methods
    def issue_copy(self) -> None:
        """Decrement available copies when borrowed."""
        if not self.is_available:
            raise ValueError(f"Cannot issue '{self.title}': No copies available in stock.")
        self.available_copies = self._available_copies - 1

    def return_copy(self) -> None:
        """Increment available copies when returned."""
        if self._available_copies >= self._total_copies:
            raise ValueError(f"Cannot return '{self.title}': All copies already in stock.")
        self.available_copies = self._available_copies + 1

    # Module I: Operator Overloading
    def __lt__(self, other: "Book") -> bool:
        """Operator Overloading (`<`): Sort books by available copies, then title."""
        if not isinstance(other, Book):
            return NotImplemented
        if self.available_copies == other.available_copies:
            return self.title.lower() < other.title.lower()
        return self.available_copies < other.available_copies

    def __add__(self, additional_copies: Union[int, "Book"]) -> "Book":
        """Operator Overloading (`+`): Add additional copies to total and available stock."""
        if isinstance(additional_copies, int):
            if additional_copies < 0:
                raise ValueError("Cannot add negative copies.")
            self._total_copies += additional_copies
            self._available_copies += additional_copies
            return self
        elif isinstance(additional_copies, Book):
            if self.book_id != additional_copies.book_id and self.title.lower() != additional_copies.title.lower():
                raise ValueError("Cannot add copies from two distinct titles.")
            self._total_copies += additional_copies.total_copies
            self._available_copies += additional_copies.available_copies
            return self
        return NotImplemented

    def __len__(self) -> int:
        """Dunder method `__len__`: Returns available physical copies."""
        return self._available_copies

    def __bool__(self) -> bool:
        """Book entity always evaluates to True in boolean contexts (distinguishing from None)."""
        return True

    def __eq__(self, other: Any) -> bool:
        """Check identity based on book_id."""
        if isinstance(other, Book):
            return self.book_id == other.book_id
        return False

    def __str__(self) -> str:
        return f"'{self.title}' by {self.author} [{self.available_copies}/{self.total_copies} available]"

    def __repr__(self) -> str:
        return (
            f"Book(id={self.book_id!r}, title={self.title!r}, author={self.author!r}, "
            f"category={self.category!r}, price={self.price}, total={self.total_copies}, "
            f"available={self.available_copies})"
        )

    # Module I: Class Methods
    @classmethod
    def from_row(cls, row: Any) -> "Book":
        """Construct Book instance from SQLite dictionary row or sqlite3.Row."""
        keys = row.keys() if hasattr(row, "keys") else row
        avail = int(row["available_copies"]) if "available_copies" in keys else int(row["total_copies"])
        return cls(
            book_id=str(row["book_id"]),
            title=str(row["title"]),
            author=str(row["author"]),
            category=str(row["category"]),
            price=float(row["price"]),
            total_copies=int(row["total_copies"]),
            available_copies=avail
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Book":
        """Construct Book instance from dictionary."""
        return cls(
            book_id=data["book_id"],
            title=data["title"],
            author=data["author"],
            category=data["category"],
            price=float(data["price"]),
            total_copies=int(data["total_copies"]),
            available_copies=int(data.get("available_copies", data["total_copies"]))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Book instance to standard dictionary."""
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "price": self.price,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies
        }
