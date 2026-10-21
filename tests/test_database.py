"""Unit tests for Database Initialization, Constraints, and Connection Management."""

import pytest
import sqlite3
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.connection import get_connection
from database.schema import init_db


class TestDatabase:
    """Test database schema initialization, foreign keys, and integrity constraints."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database file for test isolation."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_path = f.name
        
        init_db(temp_path, seed_samples=False)
        yield temp_path
        
        # Cleanup
        try:
            Path(temp_path).unlink(missing_ok=True)
        except Exception:
            pass

    def test_tables_created(self, temp_db):
        conn = get_connection(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cur.fetchall()}
        conn.close()

        assert "books" in tables
        assert "members" in tables
        assert "loans" in tables
        assert "librarians" in tables

    def test_foreign_key_enforcement(self, temp_db):
        conn = get_connection(temp_db)
        cur = conn.cursor()

        # Attempt to insert loan with non-existent book and member
        with pytest.raises(sqlite3.IntegrityError):
            cur.execute(
                """
                INSERT INTO loans (book_id, member_id, issue_date, due_date, status)
                VALUES ('NON_EXISTENT_BK', 'NON_EXISTENT_MEM', '2026-10-01', '2026-10-15', 'ACTIVE');
                """
            )
        conn.close()

    def test_stock_constraint(self, temp_db):
        conn = get_connection(temp_db)
        cur = conn.cursor()

        # Attempt to insert book with available > total
        with pytest.raises(sqlite3.IntegrityError):
            cur.execute(
                """
                INSERT INTO books (book_id, title, author, category, price, total_copies, available_copies)
                VALUES ('BK-ERR', 'Invalid Book', 'Author', 'Cat', 100.0, 2, 5);
                """
            )
        conn.close()
