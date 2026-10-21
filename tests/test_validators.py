"""Unit tests for Validators and Functional Closures."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.validators import Validators, make_range_validator


class TestValidators:
    """Test validation functions and regular expression patterns."""

    def test_valid_emails(self):
        assert Validators.is_valid_email("student@college.edu") is True
        assert Validators.is_valid_email("john.doe+app@gmail.com") is True
        assert Validators.is_valid_email("invalid-email") is False
        assert Validators.is_valid_email("@no-user.com") is False
        assert Validators.is_valid_email("missing-domain@") is False
        assert Validators.is_valid_email("") is False

    def test_valid_phones(self):
        assert Validators.is_valid_phone("9876543210") is True
        assert Validators.is_valid_phone("+919876543210") is True
        assert Validators.is_valid_phone("123-456-7890") is True
        assert Validators.is_valid_phone("12345") is False
        assert Validators.is_valid_phone("abcdefghij") is False
        assert Validators.is_valid_phone("") is False

    def test_valid_book_id(self):
        assert Validators.is_valid_book_id("BK-1001") is True
        assert Validators.is_valid_book_id("BOOK_99") is True
        assert Validators.is_valid_book_id("B") is False  # too short
        assert Validators.is_valid_book_id("BK#1001") is False  # invalid char

    def test_range_validator_closure(self):
        """Demonstrates testing the Functional Closure."""
        validator = make_range_validator(min_val=10.0, max_val=100.0, field_name="TestPrice")
        
        ok, msg = validator(50.0)
        assert ok is True
        assert msg == ""

        ok, msg = validator(5.0)
        assert ok is False
        assert "at least 10.0" in msg

        ok, msg = validator(150.0)
        assert ok is False
        assert "must not exceed 100.0" in msg

    def test_validate_book_inputs(self):
        ok, _ = Validators.validate_book_inputs("BK-01", "Python 101", "Guido", "Programming", 500.0, 5, 5)
        assert ok is True

        # Negative price
        ok, err = Validators.validate_book_inputs("BK-01", "Python 101", "Guido", "Programming", -10.0, 5)
        assert ok is False
        assert "negative" in err.lower()

        # Available > total
        ok, err = Validators.validate_book_inputs("BK-01", "Python 101", "Guido", "Programming", 500.0, 3, 5)
        assert ok is False
        assert "cannot exceed total" in err.lower()
