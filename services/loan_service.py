"""Loan Service managing circulation, issue, return, and overdue policy enforcement."""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DEFAULT_LOAN_DAYS, MAX_BOOKS_PER_MEMBER, DEFAULT_FINE_PER_DAY
from database.repositories import LoanRepository, BookRepository, MemberRepository
from models.loan import Loan
from utils.file_handlers import DataExporter
from utils.logging_config import get_logger

logger = get_logger("services.loan_service")


class LoanService:
    """Service governing book circulation with strict transaction boundaries."""

    def __init__(
        self,
        loan_repo: Optional[LoanRepository] = None,
        book_repo: Optional[BookRepository] = None,
        member_repo: Optional[MemberRepository] = None
    ):
        self.loan_repo = loan_repo or LoanRepository()
        self.book_repo = book_repo or BookRepository()
        self.member_repo = member_repo or MemberRepository()

    def issue_book(
        self,
        book_id: str,
        member_id: str,
        loan_days: int = DEFAULT_LOAN_DAYS,
        issue_date_str: Optional[str] = None
    ) -> int:
        """Issue a book to a member.
        
        Steps:
        1. Verify member exists.
        2. Verify member hasn't exceeded active loan quota.
        3. Verify book exists and has available copies.
        4. Execute atomic database transaction.
        """
        # Step 1: Member check
        member = self.member_repo.get_member_by_id(member_id)
        if not member:
            raise ValueError(f"Member '{member_id}' not found.")

        # Step 2: Quota check
        active_loans = [
            l for l in self.loan_repo.get_active_loans()
            if l["member_id"] == member_id
        ]
        if len(active_loans) >= MAX_BOOKS_PER_MEMBER:
            raise ValueError(
                f"Member '{member.name}' has reached the maximum borrowing limit ({MAX_BOOKS_PER_MEMBER} books)."
            )

        # Step 3: Book stock check
        book = self.book_repo.get_book_by_id(book_id)
        if book is None:
            raise ValueError(f"Book '{book_id}' not found.")
        if book.available_copies <= 0:
            raise ValueError(f"Book '{book.title}' is currently out of stock (0 copies available).")

        # Step 4: Dates calculation
        issue_dt = datetime.fromisoformat(issue_date_str).date() if issue_date_str else date.today()
        due_dt = issue_dt + timedelta(days=loan_days)

        # Step 5: Atomic transaction execution
        loan_id = self.loan_repo.issue_book_transaction(
            book_id=book.book_id,
            member_id=member.member_id,
            issue_date=issue_dt.isoformat(),
            due_date=due_dt.isoformat()
        )
        return loan_id

    def return_book(self, loan_id: int, return_date_str: Optional[str] = None) -> bool:
        """Return a borrowed book.
        
        Steps:
        1. Verify loan exists and is active.
        2. Prevent duplicate returns.
        3. Atomic transaction incrementing book stock and closing loan.
        """
        ret_date = return_date_str or date.today().isoformat()
        return self.loan_repo.return_book_transaction(loan_id, ret_date)

    def get_all_loans(self) -> List[Dict[str, Any]]:
        """Fetch all circulation records with joined book and member data."""
        return self.loan_repo.get_all_loans()

    def get_active_loans(self) -> List[Dict[str, Any]]:
        """Fetch all currently open loans."""
        # Refresh overdue status first
        self.loan_repo.update_overdue_statuses()
        return self.loan_repo.get_active_loans()

    def get_overdue_loans(self) -> List[Dict[str, Any]]:
        """Fetch all overdue loans with calculated fine amounts."""
        self.loan_repo.update_overdue_statuses()
        active = self.loan_repo.get_active_loans()
        today = date.today()
        overdue_list = []

        for item in active:
            try:
                due = datetime.fromisoformat(item["due_date"]).date()
                if today > due:
                    days_overdue = (today - due).days
                    item["days_overdue"] = days_overdue
                    item["fine_amount"] = round(days_overdue * DEFAULT_FINE_PER_DAY, 2)
                    overdue_list.append(item)
            except Exception:
                continue

        return overdue_list

    def export_loans(self, file_path: str, format_type: str = "CSV") -> bool:
        """Export loan transactions to CSV or JSON."""
        loans = self.get_all_loans()
        if format_type.upper() == "CSV":
            return DataExporter.export_to_csv(loans, file_path)
        elif format_type.upper() == "JSON":
            return DataExporter.export_to_json(loans, file_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
