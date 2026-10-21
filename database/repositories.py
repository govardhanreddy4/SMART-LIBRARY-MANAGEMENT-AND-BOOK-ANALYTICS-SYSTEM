"""Data Access Layer Repositories using parameterized SQL and transactional integrity."""

import sqlite3
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.connection import get_connection, get_db_cursor
from models.book import Book
from models.member import Member
from models.librarian import Librarian
from models.loan import Loan
from utils.logging_config import get_logger

logger = get_logger("database.repositories")


class BookRepository:
    """Repository handling all CRUD and search operations for Book entities."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def add_book(self, book: Book) -> bool:
        """Insert a new book record using parameterized SQL."""
        with get_db_cursor(self.db_path) as cur:
            cur.execute(
                """
                INSERT INTO books (book_id, title, author, category, price, total_copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    book.book_id,
                    book.title,
                    book.author,
                    book.category,
                    book.price,
                    book.total_copies,
                    book.available_copies
                )
            )
        logger.info("Added book: %s (%s)", book.title, book.book_id)
        return True

    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        """Retrieve a single book by its unique ID."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM books WHERE book_id = ?;", (book_id,))
            row = cur.fetchone()
            return Book.from_row(row) if row else None
        finally:
            conn.close()

    def get_all_books(self) -> List[Book]:
        """Retrieve all catalogued books."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM books ORDER BY title ASC;")
            rows = cur.fetchall()
            return [Book.from_row(r) for r in rows]
        finally:
            conn.close()

    def update_book(self, book: Book) -> bool:
        """Update existing book record."""
        with get_db_cursor(self.db_path) as cur:
            cur.execute(
                """
                UPDATE books
                SET title = ?, author = ?, category = ?, price = ?, total_copies = ?, available_copies = ?
                WHERE book_id = ?;
                """,
                (
                    book.title,
                    book.author,
                    book.category,
                    book.price,
                    book.total_copies,
                    book.available_copies,
                    book.book_id
                )
            )
        logger.info("Updated book: %s", book.book_id)
        return True

    def delete_book(self, book_id: str) -> bool:
        """Delete book if safe (no active loans or loan history breaking constraints)."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            # Check for active loans
            cur.execute("SELECT COUNT(*) FROM loans WHERE book_id = ? AND status != 'RETURNED';", (book_id,))
            active_count = cur.fetchone()[0]
            if active_count > 0:
                raise ValueError(f"Cannot delete book '{book_id}': {active_count} active loan(s) exist.")

            # Check for historical loans to protect analytical integrity
            cur.execute("SELECT COUNT(*) FROM loans WHERE book_id = ?;", (book_id,))
            hist_count = cur.fetchone()[0]
            if hist_count > 0:
                raise ValueError(
                    f"Cannot delete book '{book_id}': Has {hist_count} borrowing record(s). "
                    "Historical records must be preserved for library audits."
                )

            with conn:
                conn.execute("DELETE FROM books WHERE book_id = ?;", (book_id,))
            logger.info("Deleted book: %s", book_id)
            return True
        finally:
            conn.close()

    def search_books(self, query: str = "", category: str = "") -> List[Book]:
        """Search books by title, author, category, or book_id using parameterized query."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            params: List[Any] = []
            clauses: List[str] = []

            if query:
                pattern = f"%{query.strip()}%"
                clauses.append("(title LIKE ? OR author LIKE ? OR book_id LIKE ?)")
                params.extend([pattern, pattern, pattern])

            if category and category != "All Categories":
                clauses.append("category = ?")
                params.append(category)

            sql = "SELECT * FROM books"
            if clauses:
                sql += " WHERE " + " AND ".join(clauses)
            sql += " ORDER BY title ASC;"

            cur.execute(sql, params)
            return [Book.from_row(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def get_categories(self) -> List[str]:
        """Get distinct sorted categories."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT category FROM books ORDER BY category ASC;")
            return [row[0] for row in cur.fetchall() if row[0]]
        finally:
            conn.close()


class MemberRepository:
    """Repository handling CRUD and search for Member entities."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def add_member(self, member: Member) -> bool:
        """Insert new library member record."""
        with get_db_cursor(self.db_path) as cur:
            cur.execute(
                """
                INSERT INTO members (member_id, name, email, phone, created_at)
                VALUES (?, ?, ?, ?, ?);
                """,
                (member.member_id, member.name, member.email, member.phone, member.created_at)
            )
        logger.info("Added member: %s (%s)", member.name, member.member_id)
        return True

    def get_member_by_id(self, member_id: str) -> Optional[Member]:
        """Retrieve member by unique ID."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM members WHERE member_id = ?;", (member_id,))
            row = cur.fetchone()
            return Member.from_row(row) if row else None
        finally:
            conn.close()

    def get_all_members(self) -> List[Member]:
        """Retrieve all registered members."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM members ORDER BY name ASC;")
            return [Member.from_row(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def update_member(self, member: Member) -> bool:
        """Update existing member details."""
        with get_db_cursor(self.db_path) as cur:
            cur.execute(
                """
                UPDATE members
                SET name = ?, email = ?, phone = ?
                WHERE member_id = ?;
                """,
                (member.name, member.email, member.phone, member.member_id)
            )
        logger.info("Updated member: %s", member.member_id)
        return True

    def delete_member(self, member_id: str) -> bool:
        """Delete member safely, protecting active loans and borrowing history."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM loans WHERE member_id = ? AND status != 'RETURNED';", (member_id,))
            active_count = cur.fetchone()[0]
            if active_count > 0:
                raise ValueError(f"Cannot delete member '{member_id}': Member currently has {active_count} active loan(s).")

            cur.execute("SELECT COUNT(*) FROM loans WHERE member_id = ?;", (member_id,))
            hist_count = cur.fetchone()[0]
            if hist_count > 0:
                raise ValueError(
                    f"Cannot delete member '{member_id}': Historical loan records exist ({hist_count} records). "
                    "Member data is required for past transaction tracking."
                )

            with conn:
                conn.execute("DELETE FROM members WHERE member_id = ?;", (member_id,))
            logger.info("Deleted member: %s", member_id)
            return True
        finally:
            conn.close()

    def search_members(self, query: str = "") -> List[Member]:
        """Search members by name, member_id, email, or phone."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            pattern = f"%{query.strip()}%"
            cur.execute(
                """
                SELECT * FROM members
                WHERE name LIKE ? OR member_id LIKE ? OR email LIKE ? OR phone LIKE ?
                ORDER BY name ASC;
                """,
                (pattern, pattern, pattern, pattern)
            )
            return [Member.from_row(r) for r in cur.fetchall()]
        finally:
            conn.close()


class LoanRepository:
    """Repository managing book loans, returns, and overdue tracking with atomic transactions."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def issue_book_transaction(self, book_id: str, member_id: str, issue_date: str, due_date: str) -> int:
        """Atomically verify book availability, decrease stock, and create loan record.
        
        Guarantees:
        - Atomic execution in a single SQLite transaction
        - Rollback on failure
        - No negative inventory
        """
        conn = get_connection(self.db_path)
        try:
            with conn:
                cur = conn.cursor()
                
                # Check member exists
                cur.execute("SELECT member_id FROM members WHERE member_id = ?;", (member_id,))
                if not cur.fetchone():
                    raise ValueError(f"Member '{member_id}' not found.")

                # Check book exists and has available copies (with row lock in transaction)
                cur.execute("SELECT available_copies, total_copies, title FROM books WHERE book_id = ?;", (book_id,))
                book_row = cur.fetchone()
                if not book_row:
                    raise ValueError(f"Book '{book_id}' not found.")

                avail, total, title = book_row["available_copies"], book_row["total_copies"], book_row["title"]
                if avail <= 0:
                    raise ValueError(f"Cannot issue '{title}': 0 copies available.")

                # Decrement available copies
                cur.execute(
                    "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?;",
                    (book_id,)
                )

                # Insert loan record
                cur.execute(
                    """
                    INSERT INTO loans (book_id, member_id, issue_date, due_date, return_date, status)
                    VALUES (?, ?, ?, ?, NULL, 'ACTIVE');
                    """,
                    (book_id, member_id, issue_date, due_date)
                )
                loan_id = cur.lastrowid
                logger.info("Issued book '%s' to member '%s'. Loan ID: %s", book_id, member_id, loan_id)
                return loan_id
        finally:
            conn.close()

    def return_book_transaction(self, loan_id: int, return_date: str) -> bool:
        """Atomically mark loan returned and increment available copies.
        
        Guarantees:
        - Cannot return already-returned loan (prevents duplicate return)
        - Increases available_copies by 1
        - Ensures available_copies <= total_copies
        """
        conn = get_connection(self.db_path)
        try:
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM loans WHERE loan_id = ?;", (loan_id,))
                loan_row = cur.fetchone()
                if not loan_row:
                    raise ValueError(f"Loan #{loan_id} not found.")

                if loan_row["status"] == "RETURNED" or loan_row["return_date"] is not None:
                    raise ValueError(f"Loan #{loan_id} has already been returned on {loan_row['return_date']}.")

                book_id = loan_row["book_id"]

                # Verify current book stock before increment
                cur.execute("SELECT available_copies, total_copies FROM books WHERE book_id = ?;", (book_id,))
                b_row = cur.fetchone()
                if not b_row:
                    raise ValueError(f"Book '{book_id}' referenced by loan not found.")

                if b_row["available_copies"] >= b_row["total_copies"]:
                    raise ValueError(
                        f"Cannot return book '{book_id}': All {b_row['total_copies']} copies already in stock."
                    )

                # Update loan record
                cur.execute(
                    "UPDATE loans SET return_date = ?, status = 'RETURNED' WHERE loan_id = ?;",
                    (return_date, loan_id)
                )

                # Increment stock
                cur.execute(
                    "UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?;",
                    (book_id,)
                )
                logger.info("Returned book for Loan #%s on %s", loan_id, return_date)
                return True
        finally:
            conn.close()

    def get_loan_by_id(self, loan_id: int) -> Optional[Loan]:
        """Fetch single loan record."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM loans WHERE loan_id = ?;", (loan_id,))
            row = cur.fetchone()
            return Loan.from_row(row) if row else None
        finally:
            conn.close()

    def get_all_loans(self) -> List[Dict[str, Any]]:
        """Fetch all loans joined with book and member information."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT l.loan_id, l.book_id, b.title, l.member_id, m.name as member_name,
                       l.issue_date, l.due_date, l.return_date, l.status
                FROM loans l
                JOIN books b ON l.book_id = b.book_id
                JOIN members m ON l.member_id = m.member_id
                ORDER BY l.loan_id DESC;
                """
            )
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def get_active_loans(self) -> List[Dict[str, Any]]:
        """Fetch currently active or overdue loans."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT l.loan_id, l.book_id, b.title, l.member_id, m.name as member_name,
                       l.issue_date, l.due_date, l.return_date, l.status
                FROM loans l
                JOIN books b ON l.book_id = b.book_id
                JOIN members m ON l.member_id = m.member_id
                WHERE l.status != 'RETURNED'
                ORDER BY l.due_date ASC;
                """
            )
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def update_overdue_statuses(self, as_of_date: Optional[str] = None) -> int:
        """Mark unreturned loans past their due_date as OVERDUE."""
        today_str = as_of_date or date.today().isoformat()
        conn = get_connection(self.db_path)
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE loans
                    SET status = 'OVERDUE'
                    WHERE return_date IS NULL
                      AND due_date < ?
                      AND status = 'ACTIVE';
                    """,
                    (today_str,)
                )
                updated_count = cur.rowcount
                if updated_count > 0:
                    logger.info("Updated %d loan(s) to OVERDUE status.", updated_count)
                return updated_count
        finally:
            conn.close()


class LibrarianRepository:
    """Repository handling authentication and retrieval of Librarian staff records."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def get_by_username(self, username: str) -> Optional[Librarian]:
        """Fetch librarian account by username."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM librarians WHERE username = ?;", (username.strip().lower(),))
            row = cur.fetchone()
            return Librarian.from_row(row) if row else None
        finally:
            conn.close()

    def add_librarian(self, librarian: Librarian) -> bool:
        """Insert a new librarian record."""
        with get_db_cursor(self.db_path) as cur:
            cur.execute(
                """
                INSERT INTO librarians (librarian_id, username, password_hash, salt, name, email, phone, is_admin)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    librarian.librarian_id,
                    librarian.username,
                    librarian.password_hash,
                    librarian.salt,
                    librarian.name,
                    librarian.email,
                    librarian.phone,
                    1 if librarian.is_admin else 0
                )
            )
        return True
