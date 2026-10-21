"""Unit tests for Loan and Circulation workflows, Transactions, and Integrity Constraints."""

import pytest
import tempfile
from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.schema import init_db
from database.repositories import BookRepository, MemberRepository, LoanRepository
from services.book_service import BookService
from services.member_service import MemberService
from services.loan_service import LoanService


class TestLoans:
    """Test suite verifying Issue, Return, Stock consistency, Overdue rules, and Rollback."""

    @pytest.fixture
    def setup_services(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_path = f.name
        init_db(temp_path, seed_samples=False)

        b_repo = BookRepository(temp_path)
        m_repo = MemberRepository(temp_path)
        l_repo = LoanRepository(temp_path)

        b_service = BookService(b_repo)
        m_service = MemberService(m_repo)
        l_service = LoanService(l_repo, b_repo, m_repo)

        # Seed 1 book with 2 copies and 1 member
        b_service.add_book("BK-LOAN", "Concurrency in Python", "Expert", "Tech", 500.0, 2, 2)
        m_service.register_member("MEM-LOAN", "Kiran Rao", "kiran@college.edu", "9876543210")

        yield b_service, m_service, l_service, temp_path

        try:
            Path(temp_path).unlink(missing_ok=True)
        except Exception:
            pass

    def test_normal_issue_and_return_workflow(self, setup_services):
        b_service, m_service, l_service, _ = setup_services

        # Verify initial available copies
        book = b_service.get_book("BK-LOAN")
        assert book.available_copies == 2

        # 1. Issue book
        loan_id = l_service.issue_book(book_id="BK-LOAN", member_id="MEM-LOAN", loan_days=14)
        assert loan_id > 0

        # 2. Verify stock decreased by 1
        book = b_service.get_book("BK-LOAN")
        assert book.available_copies == 1

        # 3. Return book
        success = l_service.return_book(loan_id)
        assert success is True

        # 4. Verify stock increased by 1
        book = b_service.get_book("BK-LOAN")
        assert book.available_copies == 2

    def test_reject_issue_when_out_of_stock(self, setup_services):
        b_service, m_service, l_service, _ = setup_services

        # Register second member
        m_service.register_member("MEM-2", "Second Member", "second@college.edu", "9876543211")

        # Issue copy 1
        l_service.issue_book("BK-LOAN", "MEM-LOAN")
        # Issue copy 2
        l_service.issue_book("BK-LOAN", "MEM-2")

        # Now stock is 0
        book = b_service.get_book("BK-LOAN")
        assert book.available_copies == 0

        # Register third member and attempt issue
        m_service.register_member("MEM-3", "Third Member", "third@college.edu", "9876543212")
        with pytest.raises(ValueError) as exc:
            l_service.issue_book("BK-LOAN", "MEM-3")
        assert "out of stock" in str(exc.value).lower()

    def test_reject_duplicate_return(self, setup_services):
        _, _, l_service, _ = setup_services

        loan_id = l_service.issue_book("BK-LOAN", "MEM-LOAN")
        # First return succeeds
        assert l_service.return_book(loan_id) is True

        # Second return on same loan must be rejected
        with pytest.raises(ValueError) as exc:
            l_service.return_book(loan_id)
        assert "already been returned" in str(exc.value).lower()

    def test_reject_delete_when_active_or_historical_loans_exist(self, setup_services):
        b_service, m_service, l_service, _ = setup_services

        loan_id = l_service.issue_book("BK-LOAN", "MEM-LOAN")

        # Attempt to delete book with active loan
        with pytest.raises(ValueError):
            b_service.delete_book("BK-LOAN")

        # Attempt to delete member with active loan
        with pytest.raises(ValueError):
            m_service.delete_member("MEM-LOAN")

        # Now return loan
        l_service.return_book(loan_id)

        # Attempt to delete book with historical loan (retention policy)
        with pytest.raises(ValueError) as exc:
            b_service.delete_book("BK-LOAN")
        assert "historical records" in str(exc.value).lower()

    def test_overdue_fine_calculation(self, setup_services):
        b_service, m_service, l_service, _ = setup_services

        # Issue book with due date in the past
        past_issue = (date.today() - timedelta(days=20)).isoformat()
        past_due = (date.today() - timedelta(days=6)).isoformat()
        
        loan_id = l_service.loan_repo.issue_book_transaction(
            book_id="BK-LOAN",
            member_id="MEM-LOAN",
            issue_date=past_issue,
            due_date=past_due
        )

        overdues = l_service.get_overdue_loans()
        matching = [l for l in overdues if l["loan_id"] == loan_id]
        assert len(matching) == 1
        loan = matching[0]
        assert loan["days_overdue"] == 6
        assert loan["fine_amount"] == 12.0  # 6 days * 2.0 default fine
