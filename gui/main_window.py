"""Main Application Window with Sidebar navigation and view management."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from models.person import Person
from models.librarian import Librarian
from models.member import Member
from services.auth_service import AuthService
from services.book_service import BookService
from services.member_service import MemberService
from services.loan_service import LoanService
from services.report_service import ReportService
from concurrency.background_tasks import BackgroundTaskWorker
from config import APP_TITLE, APP_VERSION, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, THEME_COLORS
from gui.styles import UIStyleHelper
from gui.login_view import LoginView
from gui.dashboard_view import DashboardView
from gui.books_view import BooksView
from gui.members_view import MembersView
from gui.circulation_view import CirculationView
from gui.analytics_view import AnalyticsView
from gui.api_search_view import APISearchView
from gui.concurrency_view import ConcurrencyView
from utils.logging_config import get_logger

logger = get_logger("gui.main_window")


class MainWindow(tk.Tk):
    """Primary application window and view controller."""

    def __init__(self, db_path: Optional[str] = None):
        super().__init__()
        self.db_path = db_path
        self.title(f"{APP_TITLE} (v{APP_VERSION})")
        self.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")
        self.minsize(1020, 680)

        # Apply global TTK styles
        UIStyleHelper.apply_styles(self)
        self.configure(bg=THEME_COLORS["content_bg"])

        # Core Services and Background Tasks
        self.task_worker = BackgroundTaskWorker()
        self.auth_service = AuthService()
        self.book_service = BookService()
        self.member_service = MemberService()
        self.loan_service = LoanService()
        self.report_service = ReportService(db_path)

        # Poll GUI queue for safe thread updates
        self.task_worker.poll_gui_queue(self, interval_ms=100)

        self.current_user: Optional[Person] = None
        self.views: Dict[str, ttk.Frame] = {}

        self._show_login_screen()

    def _show_login_screen(self) -> None:
        """Clear window and present centered login interface."""
        for child in self.winfo_children():
            child.destroy()

        login_view = LoginView(
            parent=self,
            auth_service=self.auth_service,
            on_login_success=self._on_login_success
        )
        login_view.pack(fill="both", expand=True)

    def _on_login_success(self, user: Person) -> None:
        """Callback triggered upon successful authentication."""
        self.current_user = user
        logger.info("Session started for user: %s (Role: %s)", user.name, user.get_role_display())
        self._build_main_app_layout()

    def _build_main_app_layout(self) -> None:
        """Construct sidebar and dynamic content container."""
        for child in self.winfo_children():
            child.destroy()

        # Grid configuration: col 0 = Sidebar (fixed width), col 1 = Content (stretches)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Sidebar Navigation ---
        sidebar = tk.Frame(self, bg=THEME_COLORS["sidebar_bg"], width=230)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.pack_propagate(False)

        # Brand Title
        brand_frame = tk.Frame(sidebar, bg=THEME_COLORS["sidebar_bg"], padx=16, pady=20)
        brand_frame.pack(fill="x")

        tk.Label(
            brand_frame,
            text="📚 SmartLibrary",
            font=(UIStyleHelper.FONT_FAMILY, 15, "bold"),
            bg=THEME_COLORS["sidebar_bg"],
            fg="#FFFFFF"
        ).pack(anchor="w")

        tk.Label(
            brand_frame,
            text="Analytics & Circulation",
            font=UIStyleHelper.FONT_SMALL,
            bg=THEME_COLORS["sidebar_bg"],
            fg="#94A3B8"
        ).pack(anchor="w")

        # Current User Pill
        user_pill = tk.Frame(sidebar, bg="#334155", padx=12, pady=10)
        user_pill.pack(fill="x", padx=12, pady=(0, 16))

        tk.Label(
            user_pill,
            text=f"👤 {self.current_user.name}",
            font=UIStyleHelper.FONT_SUBHEADER,
            bg="#334155",
            fg="#F8FAFC"
        ).pack(anchor="w")

        tk.Label(
            user_pill,
            text=self.current_user.get_role_display(),
            font=UIStyleHelper.FONT_SMALL,
            bg="#334155",
            fg="#38BDF8"
        ).pack(anchor="w")

        # Navigation Buttons
        nav_items = [
            ("dashboard", "📊 Dashboard"),
            ("books", "📚 Book Inventory"),
            ("members", "👥 Members Directory"),
            ("circulation", "🔄 Circulation Desk"),
            ("analytics", "📈 Analytics & Charts"),
            ("api_search", "🌐 Google Books API"),
            ("concurrency", "⚡ Performance Bench"),
        ]

        self.nav_buttons: Dict[str, tk.Button] = {}
        for key, text in nav_items:
            btn = tk.Button(
                sidebar,
                text=f"  {text}",
                font=UIStyleHelper.FONT_SUBHEADER,
                bg=THEME_COLORS["sidebar_bg"],
                fg="#F1F5F9",
                activebackground=THEME_COLORS["primary"],
                activeforeground="#FFFFFF",
                bd=0,
                anchor="w",
                padx=16,
                pady=10,
                command=lambda k=key: self.switch_view(k)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        # Spacer to push logout button to bottom
        spacer = tk.Frame(sidebar, bg=THEME_COLORS["sidebar_bg"])
        spacer.pack(fill="both", expand=True)

        # Logout Button
        logout_btn = tk.Button(
            sidebar,
            text="  🚪 Log Out",
            font=UIStyleHelper.FONT_SUBHEADER,
            bg="#475569",
            fg="#FFFFFF",
            activebackground=THEME_COLORS["danger"],
            activeforeground="#FFFFFF",
            bd=0,
            anchor="w",
            padx=16,
            pady=10,
            command=self._handle_logout
        )
        logout_btn.pack(fill="x", padx=12, pady=16)

        # --- Dynamic Content Frame ---
        self.content_container = tk.Frame(self, bg=THEME_COLORS["content_bg"])
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.columnconfigure(0, weight=1)
        self.content_container.rowconfigure(0, weight=1)

        # Instantiate all views
        self.views["dashboard"] = DashboardView(self.content_container, self.report_service, on_navigate=self.switch_view, db_path=self.db_path)
        self.views["books"] = BooksView(self.content_container, self.book_service, on_data_changed=self._on_data_updated)
        self.views["members"] = MembersView(self.content_container, self.member_service, on_data_changed=self._on_data_updated)
        self.views["circulation"] = CirculationView(self.content_container, self.loan_service, self.book_service, self.member_service, on_data_changed=self._on_data_updated)
        self.views["analytics"] = AnalyticsView(self.content_container, db_path=self.db_path)
        self.views["api_search"] = APISearchView(self.content_container, self.book_service, self.task_worker, on_data_changed=self._on_data_updated)
        self.views["concurrency"] = ConcurrencyView(self.content_container, self.task_worker)

        # Show Dashboard initially
        self.switch_view("dashboard")

    def switch_view(self, view_key: str) -> None:
        """Switch active visible view in the content container."""
        if view_key not in self.views:
            return

        # Hide all views
        for k, v in self.views.items():
            v.grid_remove()
            if k in self.nav_buttons:
                self.nav_buttons[k].config(bg=THEME_COLORS["sidebar_bg"], fg="#F1F5F9")

        # Display selected view
        target_view = self.views[view_key]
        target_view.grid(row=0, column=0, sticky="nsew")
        if view_key in self.nav_buttons:
            self.nav_buttons[view_key].config(bg=THEME_COLORS["primary"], fg="#FFFFFF")

        # Auto-refresh data if switching to dashboard or analytics
        if view_key == "dashboard":
            self.views["dashboard"].refresh_dashboard()
        elif view_key == "analytics":
            self.views["analytics"].refresh_analytics()

    def _on_data_updated(self) -> None:
        """Callback triggered whenever books, members, or loans are mutated."""
        logger.info("Catalog mutation detected. Refreshing active operational views.")
        if "dashboard" in self.views:
            self.views["dashboard"].refresh_dashboard()
        if "books" in self.views:
            self.views["books"].load_books()
        if "members" in self.views:
            self.views["members"].load_members()
        if "circulation" in self.views:
            self.views["circulation"].load_loans()

    def _handle_logout(self) -> None:
        """Log out user and return to login screen."""
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?")
        if confirm:
            self.auth_service.logout()
            self.current_user = None
            self._show_login_screen()
