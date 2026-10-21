"""Loan model representing book circulation records."""

from datetime import datetime, date
from typing import Dict, Any, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DEFAULT_FINE_PER_DAY


class Loan:
    """Represents a borrowing transaction record.
    
    Demonstrates:
    - Module I: Object-Oriented Modeling of Business Entity
    - Module I: Special methods (__repr__, __str__, __eq__)
    - Module I: Class method for row factory instantiation
    - Date calculations and overdue state determination
    """

    STATUS_ACTIVE = "ACTIVE"
    STATUS_RETURNED = "RETURNED"
    STATUS_OVERDUE = "OVERDUE"

    def __init__(
        self,
        loan_id: Optional[int],
        book_id: str,
        member_id: str,
        issue_date: str,
        due_date: str,
        return_date: Optional[str] = None,
        status: str = STATUS_ACTIVE
    ):
        self.loan_id = loan_id
        self.book_id = str(book_id).strip()
        self.member_id = str(member_id).strip()
        self.issue_date = str(issue_date).strip()
        self.due_date = str(due_date).strip()
        self.return_date = str(return_date).strip() if return_date else None
        self.status = status.upper()

    @property
    def is_active(self) -> bool:
        """Check if loan is currently unreturned."""
        return self.return_date is None and self.status in (self.STATUS_ACTIVE, self.STATUS_OVERDUE)

    def is_overdue(self, as_of_date: Optional[date] = None) -> bool:
        """Check if loan is currently overdue."""
        if self.return_date is not None:
            return False  # Returned loans are closed
        
        check_date = as_of_date or date.today()
        try:
            due = datetime.fromisoformat(self.due_date).date()
            return check_date > due
        except Exception:
            return False

    def calculate_overdue_days(self, as_of_date: Optional[date] = None) -> int:
        """Calculate number of days past due date."""
        if self.return_date is not None:
            # Check if it was returned late
            try:
                ret = datetime.fromisoformat(self.return_date).date()
                due = datetime.fromisoformat(self.due_date).date()
                return max(0, (ret - due).days)
            except Exception:
                return 0

        check_date = as_of_date or date.today()
        try:
            due = datetime.fromisoformat(self.due_date).date()
            return max(0, (check_date - due).days)
        except Exception:
            return 0

    def calculate_fine(self, rate_per_day: float = DEFAULT_FINE_PER_DAY) -> float:
        """Calculate fine incurred for overdue period."""
        days = self.calculate_overdue_days()
        return round(days * rate_per_day, 2)

    def mark_returned(self, return_date: Optional[str] = None) -> None:
        """Update loan state when book is returned."""
        if not self.is_active:
            raise ValueError(f"Loan #{self.loan_id} is already returned on {self.return_date}.")
        
        self.return_date = return_date or datetime.now().date().isoformat()
        self.status = self.STATUS_RETURNED

    @classmethod
    def from_row(cls, row: Any) -> "Loan":
        """Instantiate Loan from SQLite dictionary row or sqlite3.Row."""
        keys = row.keys() if hasattr(row, "keys") else row
        loan_id = int(row["loan_id"]) if "loan_id" in keys and row["loan_id"] is not None else None
        ret_date = str(row["return_date"]) if "return_date" in keys and row["return_date"] else None
        status = str(row["status"]) if "status" in keys else cls.STATUS_ACTIVE
        return cls(
            loan_id=loan_id,
            book_id=str(row["book_id"]),
            member_id=str(row["member_id"]),
            issue_date=str(row["issue_date"]),
            due_date=str(row["due_date"]),
            return_date=ret_date,
            status=status
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Loan instance to dictionary."""
        return {
            "loan_id": self.loan_id,
            "book_id": self.book_id,
            "member_id": self.member_id,
            "issue_date": self.issue_date,
            "due_date": self.due_date,
            "return_date": self.return_date,
            "status": self.status
        }

    def __repr__(self) -> str:
        return (
            f"Loan(id={self.loan_id}, book={self.book_id!r}, member={self.member_id!r}, "
            f"due={self.due_date}, status={self.status!r})"
        )

    def __str__(self) -> str:
        ret_info = f" (Returned: {self.return_date})" if self.return_date else ""
        return f"Loan #{self.loan_id}: Book '{self.book_id}' to Member '{self.member_id}' [Due: {self.due_date}]{ret_info}"
