"""End-to-End Workflow Integration Test as required by Section 10."""

import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.schema import init_db
from database.repositories import BookRepository, MemberRepository, LoanRepository
from services.book_service import BookService
from services.member_service import MemberService
from services.loan_service import LoanService
from services.report_service import ReportService
from analytics.data_processor import DataProcessor


class TestEndToEndWorkflow:
    """Verifies the complete life-cycle required by Section 10 of Master Prompt:
    
    1. Start the service layer.
    2. Create a book with multiple copies.
    3. Register a member.
    4. Issue one copy.
    5. Verify the available count decreases.
    6. Return the loan.
    7. Verify the available count increases.
    8. Verify the loan history remains correct.
    9. Verify dashboard and analytics results reflect the final data.
    """

    def test_complete_circulation_and_analytics_lifecycle(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_db_path = f.name

        try:
            # Step 1: Start service layer with clean database
            init_db(temp_db_path, seed_samples=False)
            b_repo = BookRepository(temp_db_path)
            m_repo = MemberRepository(temp_db_path)
            l_repo = LoanRepository(temp_db_path)

            book_service = BookService(b_repo)
            member_service = MemberService(m_repo)
            loan_service = LoanService(l_repo, b_repo, m_repo)
            report_service = ReportService(temp_db_path)
            data_processor = DataProcessor(temp_db_path)

            # Step 2: Create a book with multiple copies (total=3, available=3)
            book = book_service.add_book(
                book_id="BK-E2E-101",
                title="Advanced Python Programming",
                author="Course Team",
                category="Computer Science",
                price=850.0,
                total_copies=3,
                available_copies=3
            )
            assert book.total_copies == 3
            assert book.available_copies == 3

            # Step 3: Register a member
            member = member_service.register_member(
                member_id="MEM-E2E-201",
                name="Vikram Seth",
                email="vikram.seth@college.edu",
                phone="9876543210"
            )
            assert member.member_id == "MEM-E2E-201"

            # Step 4: Issue one copy
            loan_id = loan_service.issue_book(
                book_id="BK-E2E-101",
                member_id="MEM-E2E-201",
                loan_days=14
            )
            assert loan_id > 0

            # Step 5: Verify the available count decreases (3 -> 2)
            book_after_issue = book_service.get_book("BK-E2E-101")
            assert book_after_issue.available_copies == 2
            assert book_after_issue.issued_copies == 1

            # Verify intermediate dashboard state
            mid_summary = report_service.get_dashboard_summary()
            assert mid_summary["total_titles"] == 1
            assert mid_summary["total_copies"] == 3
            assert mid_summary["available_copies"] == 2
            assert mid_summary["issued_copies"] == 1
            assert mid_summary["active_members"] == 1

            # Step 6: Return the loan
            return_ok = loan_service.return_book(loan_id)
            assert return_ok is True

            # Step 7: Verify the available count increases (2 -> 3)
            book_after_return = book_service.get_book("BK-E2E-101")
            assert book_after_return.available_copies == 3
            assert book_after_return.issued_copies == 0

            # Step 8: Verify the loan history remains correct
            all_loans = loan_service.get_all_loans()
            assert len(all_loans) == 1
            historic_loan = all_loans[0]
            assert historic_loan["loan_id"] == loan_id
            assert historic_loan["status"] == "RETURNED"
            assert historic_loan["return_date"] is not None

            # Step 9: Verify dashboard and analytics results reflect the final data
            final_summary = report_service.get_dashboard_summary()
            assert final_summary["total_titles"] == 1
            assert final_summary["total_copies"] == 3
            assert final_summary["available_copies"] == 3
            assert final_summary["issued_copies"] == 0
            assert final_summary["active_members"] == 1

            # Verify Pandas & NumPy analysis reflections
            cat_df = data_processor.get_category_analytics()
            assert len(cat_df) == 1
            assert cat_df.iloc[0]["category"] == "Computer Science"
            assert cat_df.iloc[0]["total_copies"] == 3
            assert cat_df.iloc[0]["available_copies"] == 3

            price_stats = data_processor.calculate_price_statistics_numpy()
            assert price_stats["count"] == 1
            assert price_stats["mean"] == 850.0

        finally:
            try:
                Path(temp_db_path).unlink(missing_ok=True)
            except Exception:
                pass
