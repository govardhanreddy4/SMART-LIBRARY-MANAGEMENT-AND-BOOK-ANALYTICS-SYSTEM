"""Smoke tests verifying that Tkinter GUI components and windows instantiate cleanly."""

import pytest
import tkinter as tk
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.schema import init_db
from gui.main_window import MainWindow
from services.auth_service import AuthService
from services.book_service import BookService
from services.member_service import MemberService
from services.loan_service import LoanService
from services.report_service import ReportService
from concurrency.background_tasks import BackgroundTaskWorker
from gui.login_view import LoginView
from gui.dashboard_view import DashboardView
from gui.books_view import BooksView
from gui.members_view import MembersView
from gui.circulation_view import CirculationView
from gui.analytics_view import AnalyticsView
from gui.api_search_view import APISearchView
from gui.concurrency_view import ConcurrencyView


class TestGUIComponents:
    """Verifies that all GUI views and dialogs construct cleanly without exceptions."""

    @pytest.fixture(scope="module")
    def tk_root(self):
        """Single module-level Tk root window for all view instantiation tests."""
        try:
            root = tk.Tk()
            root.withdraw()  # Headless mode: hide root window
            yield root
            root.destroy()
        except tk.TclError:
            pytest.skip("Tkinter graphical display is not available.")

    @pytest.fixture(scope="module")
    def test_db(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_path = f.name
        init_db(temp_path, seed_samples=True)
        yield temp_path
        try:
            Path(temp_path).unlink(missing_ok=True)
        except Exception:
            pass

    def test_login_view_instantiation(self, tk_root):
        auth_service = AuthService()
        view = LoginView(tk_root, auth_service, lambda user: None)
        assert view is not None
        view.destroy()

    def test_dashboard_view_instantiation(self, tk_root, test_db):
        report_service = ReportService(test_db)
        view = DashboardView(tk_root, report_service, db_path=test_db)
        assert view is not None
        view.destroy()

    def test_books_view_instantiation(self, tk_root, test_db):
        from database.repositories import BookRepository
        b_service = BookService(BookRepository(test_db))
        view = BooksView(tk_root, b_service)
        assert view is not None
        view.destroy()

    def test_members_view_instantiation(self, tk_root, test_db):
        from database.repositories import MemberRepository
        m_service = MemberService(MemberRepository(test_db))
        view = MembersView(tk_root, m_service)
        assert view is not None
        view.destroy()

    def test_circulation_view_instantiation(self, tk_root, test_db):
        from database.repositories import BookRepository, MemberRepository, LoanRepository
        l_repo = LoanRepository(test_db)
        b_repo = BookRepository(test_db)
        m_repo = MemberRepository(test_db)
        view = CirculationView(
            tk_root,
            LoanService(l_repo, b_repo, m_repo),
            BookService(b_repo),
            MemberService(m_repo)
        )
        assert view is not None
        view.destroy()

    def test_analytics_view_instantiation(self, tk_root, test_db):
        view = AnalyticsView(tk_root, db_path=test_db)
        assert view is not None
        view.destroy()

    def test_api_search_view_instantiation(self, tk_root, test_db):
        from database.repositories import BookRepository
        b_service = BookService(BookRepository(test_db))
        worker = BackgroundTaskWorker()
        view = APISearchView(tk_root, b_service, worker)
        assert view is not None
        view.destroy()

    def test_concurrency_view_instantiation(self, tk_root):
        worker = BackgroundTaskWorker()
        view = ConcurrencyView(tk_root, worker)
        assert view is not None
        view.destroy()
