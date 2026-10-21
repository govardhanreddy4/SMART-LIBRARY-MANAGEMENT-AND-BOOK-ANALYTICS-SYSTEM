"""Data validation utilities demonstrating Regular Expressions and Functional Closures."""

import re
from typing import Tuple, Optional, Callable, Any


class ValidationError(ValueError):
    """Raised when data validation fails."""
    pass


# Compiled Regular Expression Patterns for performance
# Module IV: Regular Expressions
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?(\d{1,3})?[-.\s]?(\d{10}|\d{3}[-.\s]\d{3}[-.\s]\d{4})$")
ISBN_REGEX = re.compile(r"^(?:ISBN(?:-1[03])?:?\ )?(?=[0-9X]{10}$|(?=(?:[0-9]+[-\ ]){3})[-\ 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[-\ ]){4})[-\ 0-9]{17}$)(?:97[89][-\ ]?)?[0-9]{1,5}[-\ ]?[0-9]+[-\ ]?[0-9]+[-\ ]?[0-9X]$")
BOOK_ID_REGEX = re.compile(r"^[A-Za-z0-9_-]{2,20}$")


# Module II: Closure & Higher-Order Function Demonstration
def make_range_validator(min_val: float, max_val: Optional[float] = None, field_name: str = "Field") -> Callable[[float], Tuple[bool, str]]:
    """Higher-Order Function returning a Closure to validate numeric ranges.
    
    Demonstrates:
    - Closure: captures `min_val`, `max_val`, and `field_name` from enclosing scope.
    - Higher-Order Function: returns a specialized validator function.
    """
    def validator(val: float) -> Tuple[bool, str]:
        if val < min_val:
            return False, f"{field_name} must be at least {min_val}."
        if max_val is not None and val > max_val:
            return False, f"{field_name} must not exceed {max_val}."
        return True, ""
    return validator


class Validators:
    """Central validation suite demonstrating Static Methods, Regex, and Functional validation."""

    # Static instance of range validator using the closure
    price_validator = staticmethod(make_range_validator(0.0, 100000.0, "Price"))
    stock_validator = staticmethod(make_range_validator(0, 10000, "Copies"))

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format using regular expressions."""
        if not email or not isinstance(email, str):
            return False
        return bool(EMAIL_REGEX.match(email.strip()))

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validate phone number using regular expressions."""
        if not phone or not isinstance(phone, str):
            return False
        return bool(PHONE_REGEX.match(phone.strip()))

    @staticmethod
    def is_valid_isbn(isbn: str) -> bool:
        """Validate ISBN-10 or ISBN-13 format."""
        if not isbn or not isinstance(isbn, str):
            return False
        cleaned = isbn.replace("-", "").replace(" ", "").upper()
        # Basic check against regex
        return bool(ISBN_REGEX.match(isbn.strip()) or (len(cleaned) in (10, 13) and cleaned[:-1].isdigit()))

    @staticmethod
    def is_valid_book_id(book_id: str) -> bool:
        """Validate book ID format."""
        if not book_id or not isinstance(book_id, str):
            return False
        return bool(BOOK_ID_REGEX.match(book_id.strip()))

    @classmethod
    def validate_book_inputs(
        cls,
        book_id: str,
        title: str,
        author: str,
        category: str,
        price: float,
        total_copies: int,
        available_copies: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """Validate all fields for a book record.
        
        Demonstrates Class Method.
        """
        if not book_id or not book_id.strip():
            return False, "Book ID is required."
        if not cls.is_valid_book_id(book_id):
            return False, "Book ID must be 2-20 alphanumeric characters, hyphens, or underscores."
        if not title or not title.strip():
            return False, "Book title cannot be empty."
        if not author or not author.strip():
            return False, "Author cannot be empty."
        if not category or not category.strip():
            return False, "Category cannot be empty."

        try:
            p = float(price)
            if p < 0:
                return False, "Price cannot be negative."
        except (ValueError, TypeError):
            return False, "Price must be a valid number."

        try:
            total = int(total_copies)
            if total <= 0:
                return False, "Total copies must be at least 1."
        except (ValueError, TypeError):
            return False, "Total copies must be a valid integer."

        if available_copies is not None:
            try:
                avail = int(available_copies)
                if avail < 0:
                    return False, "Available copies cannot be negative."
                if avail > total:
                    return False, f"Available copies ({avail}) cannot exceed total copies ({total})."
            except (ValueError, TypeError):
                return False, "Available copies must be a valid integer."

        return True, None

    @classmethod
    def validate_member_inputs(
        cls,
        member_id: str,
        name: str,
        email: str,
        phone: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate all fields for a member record."""
        if not member_id or not member_id.strip():
            return False, "Member ID is required."
        if not name or not name.strip() or len(name.strip()) < 2:
            return False, "Member name must be at least 2 characters."
        if not cls.is_valid_email(email):
            return False, "Invalid email address format."
        if not cls.is_valid_phone(phone):
            return False, "Invalid phone number format (e.g., 9876543210 or +919876543210)."

        return True, None
