"""Reporting Service generating operational summaries and exportable reports."""

from datetime import date
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.connection import get_connection
from utils.file_handlers import DataExporter
from utils.logging_config import get_logger

logger = get_logger("services.report_service")


class ReportService:
    """Provides high-level operational statistics and reporting."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def get_dashboard_summary(self) -> Dict[str, int]:
        """Compute live key metrics calculated strictly from actual database records.
        
        Definitions:
        - total_titles: count of distinct catalogued book entries
        - total_copies: sum of physical book inventory
        - available_copies: physical copies currently on shelves
        - issued_copies: total_copies - available_copies (physical books in circulation)
        - active_members: total registered library members
        - overdue_loans: active loans whose due_date < today (subset of active loans)
        """
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            
            # Book counts
            cur.execute(
                """
                SELECT COUNT(*), COALESCE(SUM(total_copies), 0), COALESCE(SUM(available_copies), 0)
                FROM books;
                """
            )
            row_books = cur.fetchone()
            total_titles = row_books[0]
            total_copies = row_books[1]
            available_copies = row_books[2]
            issued_copies = max(0, total_copies - available_copies)

            # Member count
            cur.execute("SELECT COUNT(*) FROM members;")
            active_members = cur.fetchone()[0]

            # Overdue loans count (subset of currently active loans)
            today_str = date.today().isoformat()
            cur.execute(
                """
                SELECT COUNT(*) FROM loans
                WHERE return_date IS NULL AND due_date < ?;
                """,
                (today_str,)
            )
            overdue_loans = cur.fetchone()[0]

            return {
                "total_titles": total_titles,
                "total_copies": total_copies,
                "available_copies": available_copies,
                "issued_copies": issued_copies,
                "active_members": active_members,
                "overdue_loans": overdue_loans
            }
        finally:
            conn.close()

    def get_category_breakdown(self) -> List[Dict[str, Any]]:
        """Get inventory and title statistics grouped by category."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT category,
                       COUNT(*) as title_count,
                       SUM(total_copies) as total_copies,
                       SUM(available_copies) as available_copies,
                       SUM(price * total_copies) as total_valuation
                FROM books
                GROUP BY category
                ORDER BY total_copies DESC;
                """
            )
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def get_popular_books(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently borrowed books."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT b.book_id, b.title, b.author, b.category, COUNT(l.loan_id) as borrow_count
                FROM books b
                LEFT JOIN loans l ON b.book_id = l.book_id
                GROUP BY b.book_id, b.title, b.author, b.category
                ORDER BY borrow_count DESC, b.title ASC
                LIMIT ?;
                """,
                (limit,)
            )
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def export_summary_report(self, file_path: str, format_type: str = "JSON") -> bool:
        """Export comprehensive library status report."""
        summary = self.get_dashboard_summary()
        cat_breakdown = self.get_category_breakdown()
        popular = self.get_popular_books(10)

        report_data = [{
            "metric": k,
            "value": v
        } for k, v in summary.items()]

        fmt = format_type.upper()
        if fmt == "CSV":
            return DataExporter.export_to_csv(report_data, file_path)
        elif fmt == "JSON":
            full_data = [{
                "summary": summary,
                "categories": cat_breakdown,
                "popular_books": popular
            }]
            return DataExporter.export_to_json(full_data, file_path)
        elif fmt == "XML":
            return DataExporter.export_to_xml(report_data, file_path, "library_report", "metric_item")
        return False
