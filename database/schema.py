"""Database Schema DDL and Initialization Routines."""

import sqlite3
from pathlib import Path
from typing import Optional, Union
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.connection import get_connection
from models.librarian import Librarian
from utils.logging_config import get_logger

logger = get_logger("database.schema")

SCHEMA_SQL = """
-- Books Table
CREATE TABLE IF NOT EXISTS books (
    book_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL CHECK(price >= 0),
    total_copies INTEGER NOT NULL CHECK(total_copies >= 1),
    available_copies INTEGER NOT NULL CHECK(available_copies >= 0 AND available_copies <= total_copies)
);

-- Members Table
CREATE TABLE IF NOT EXISTS members (
    member_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Librarians (Admin/Staff) Table
CREATE TABLE IF NOT EXISTS librarians (
    librarian_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 1
);

-- Circulation Loans Table
CREATE TABLE IF NOT EXISTS loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL,
    member_id TEXT NOT NULL,
    issue_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    return_date TEXT,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'RETURNED', 'OVERDUE')),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE RESTRICT,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE RESTRICT
);

-- Performance Optimization Indexes
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);
CREATE INDEX IF NOT EXISTS idx_loans_book_id ON loans(book_id);
CREATE INDEX IF NOT EXISTS idx_loans_member_id ON loans(member_id);
CREATE INDEX IF NOT EXISTS idx_loans_dates ON loans(issue_date, due_date);
"""

# Realistic Sample Data for Initial Demonstration
INITIAL_BOOKS = [
    ("BK-1001", "Clean Code: A Handbook of Agile Software Craftsmanship", "Robert C. Martin", "Computer Science", 650.0, 5, 4),
    ("BK-1002", "Introduction to Algorithms (CLRS)", "Thomas H. Cormen", "Computer Science", 1200.0, 4, 3),
    ("BK-1003", "Design Patterns: Elements of Reusable Object-Oriented Software", "Erich Gamma et al.", "Software Engineering", 750.0, 3, 2),
    ("BK-1004", "Python Crash Course: A Hands-On Guide", "Eric Matthes", "Programming", 450.0, 6, 5),
    ("BK-1005", "Fluent Python: Clear, Concise, and Effective Programming", "Luciano Ramalho", "Programming", 890.0, 4, 3),
    ("BK-1006", "Artificial Intelligence: A Modern Approach", "Stuart Russell, Peter Norvig", "Artificial Intelligence", 1450.0, 3, 2),
    ("BK-1007", "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow", "Aurélien Géron", "Data Science", 980.0, 5, 4),
    ("BK-1008", "Deep Learning", "Ian Goodfellow, Yoshua Bengio", "Artificial Intelligence", 1300.0, 3, 2),
    ("BK-1009", "Database System Concepts", "Abraham Silberschatz", "Databases", 850.0, 5, 4),
    ("BK-1010", "Computer Networks: A Systems Approach", "Larry L. Peterson", "Networking", 720.0, 4, 3),
]

INITIAL_MEMBERS = [
    ("MEM-001", "Aarav Sharma", "aarav.sharma@college.edu", "+919876543210", "2026-08-01T10:00:00"),
    ("MEM-002", "Priya Patel", "priya.patel@college.edu", "+919876543211", "2026-08-05T11:30:00"),
    ("MEM-003", "Rohan Verma", "rohan.verma@college.edu", "+919876543212", "2026-08-10T14:15:00"),
    ("MEM-004", "Sneha Iyer", "sneha.iyer@college.edu", "+919876543213", "2026-08-15T09:45:00"),
    ("MEM-005", "Ananya Gupta", "ananya.gupta@college.edu", "+919876543214", "2026-09-01T16:20:00"),
]

INITIAL_LOANS = [
    # Active normal loan
    (1, "BK-1001", "MEM-001", "2026-10-10", "2026-10-24", None, "ACTIVE"),
    # Active overdue loan (past due date)
    (2, "BK-1002", "MEM-002", "2026-09-20", "2026-10-04", None, "OVERDUE"),
    # Returned loan
    (3, "BK-1003", "MEM-003", "2026-09-01", "2026-09-15", "2026-09-14", "RETURNED"),
    # Active loan
    (4, "BK-1004", "MEM-004", "2026-10-12", "2026-10-26", None, "ACTIVE"),
    # Active overdue loan
    (5, "BK-1005", "MEM-005", "2026-09-25", "2026-10-09", None, "OVERDUE"),
]


def init_db(db_path: Optional[Union[str, Path]] = None, seed_samples: bool = True) -> None:
    """Initialize SQLite database with full schema, default admin, and starter data."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.executescript(SCHEMA_SQL)
            
            # Check if default librarian exists
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM librarians WHERE username = 'admin';")
            if cur.fetchone()[0] == 0:
                pwd_hash, salt = Librarian.hash_password("admin123")
                cur.execute(
                    """
                    INSERT INTO librarians (librarian_id, username, password_hash, salt, name, email, phone, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1);
                    """,
                    ("LIB-001", "admin", pwd_hash, salt, "Chief Librarian", "admin@library.college.edu", "+919876543200")
                )
                logger.info("Created default administrator account: username='admin', password='admin123'")

            # Seed sample catalog if empty and requested
            if seed_samples:
                cur.execute("SELECT COUNT(*) FROM books;")
                if cur.fetchone()[0] == 0:
                    cur.executemany(
                        """
                        INSERT INTO books (book_id, title, author, category, price, total_copies, available_copies)
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                        """,
                        INITIAL_BOOKS
                    )
                    logger.info("Seeded %d initial book records.", len(INITIAL_BOOKS))

                cur.execute("SELECT COUNT(*) FROM members;")
                if cur.fetchone()[0] == 0:
                    cur.executemany(
                        """
                        INSERT INTO members (member_id, name, email, phone, created_at)
                        VALUES (?, ?, ?, ?, ?);
                        """,
                        INITIAL_MEMBERS
                    )
                    logger.info("Seeded %d initial member records.", len(INITIAL_MEMBERS))

                cur.execute("SELECT COUNT(*) FROM loans;")
                if cur.fetchone()[0] == 0:
                    cur.executemany(
                        """
                        INSERT INTO loans (loan_id, book_id, member_id, issue_date, due_date, return_date, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                        """,
                        INITIAL_LOANS
                    )
                    logger.info("Seeded %d initial circulation records.", len(INITIAL_LOANS))

        logger.info("Database schema initialized successfully.")
    finally:
        conn.close()
