"""Login View providing secure authentication and role selection."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from services.auth_service import AuthService
from models.person import Person
from config import THEME_COLORS
from gui.styles import UIStyleHelper
from utils.logging_config import get_logger

logger = get_logger("gui.login_view")


class LoginView(ttk.Frame):
    """Modern authentication screen with credential validation and role assignment."""

    def __init__(self, parent: tk.Widget, auth_service: AuthService, on_login_success: Callable[[Person], None]):
        super().__init__(parent)
        self.auth_service = auth_service
        self.on_login_success = on_login_success

        self.configure(style="TFrame")
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct centered card layout for login."""
        # Center grid weighting
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Main Card container
        card = ttk.Frame(self, style="Card.TFrame", padding=36)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.columnconfigure(0, weight=1)

        # Header Icon / Title
        title_lbl = tk.Label(
            card,
            text="📚 Smart Library System",
            font=(UIStyleHelper.FONT_FAMILY, 18, "bold"),
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["primary"]
        )
        title_lbl.grid(row=0, column=0, pady=(0, 6))

        subtitle_lbl = tk.Label(
            card,
            text="Advanced Python Programming — College Micro-Project",
            font=UIStyleHelper.FONT_SMALL,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["text_muted"]
        )
        subtitle_lbl.grid(row=1, column=0, pady=(0, 24))

        # Role Selection Radio Buttons
        self.role_var = tk.StringVar(value="LIBRARIAN")
        role_frame = tk.Frame(card, bg=THEME_COLORS["card_bg"])
        role_frame.grid(row=2, column=0, pady=(0, 16), sticky="w")

        tk.Label(
            role_frame,
            text="Select Portal Role:",
            font=UIStyleHelper.FONT_SUBHEADER,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 4))

        rb_frame = tk.Frame(role_frame, bg=THEME_COLORS["card_bg"])
        rb_frame.pack(anchor="w")

        r1 = tk.Radiobutton(
            rb_frame,
            text="Librarian / Staff (Admin)",
            variable=self.role_var,
            value="LIBRARIAN",
            command=self._on_role_change,
            bg=THEME_COLORS["card_bg"],
            font=UIStyleHelper.FONT_BODY,
            activebackground=THEME_COLORS["card_bg"]
        )
        r1.pack(side="left", padx=(0, 12))

        r2 = tk.Radiobutton(
            rb_frame,
            text="Student / Member",
            variable=self.role_var,
            value="STUDENT",
            command=self._on_role_change,
            bg=THEME_COLORS["card_bg"],
            font=UIStyleHelper.FONT_BODY,
            activebackground=THEME_COLORS["card_bg"]
        )
        r2.pack(side="left")

        # Username / ID field
        self.id_label = tk.Label(
            card,
            text="Username:",
            font=UIStyleHelper.FONT_SUBHEADER,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["text_dark"]
        )
        self.id_label.grid(row=3, column=0, sticky="w", pady=(0, 4))

        self.username_entry = ttk.Entry(card, width=32, font=UIStyleHelper.FONT_BODY)
        self.username_entry.grid(row=4, column=0, sticky="ew", pady=(0, 14))
        self.username_entry.insert(0, "admin")

        # Password field (for Librarian)
        self.pwd_label = tk.Label(
            card,
            text="Password:",
            font=UIStyleHelper.FONT_SUBHEADER,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["text_dark"]
        )
        self.pwd_label.grid(row=5, column=0, sticky="w", pady=(0, 4))

        self.password_entry = ttk.Entry(card, width=32, show="•", font=UIStyleHelper.FONT_BODY)
        self.password_entry.grid(row=6, column=0, sticky="ew", pady=(0, 16))
        self.password_entry.insert(0, "admin123")

        # Error message label
        self.error_label = tk.Label(
            card,
            text="",
            font=UIStyleHelper.FONT_SMALL,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["danger"]
        )
        self.error_label.grid(row=7, column=0, pady=(0, 10))

        # Login Submit Button
        self.login_btn = ttk.Button(card, text="Log In", style="TButton", command=self._handle_login)
        self.login_btn.grid(row=8, column=0, sticky="ew", pady=(0, 16))

        # Default Credentials Hint Box
        hint_box = tk.Label(
            card,
            text="💡 Default Admin Credentials:\nUsername: admin  |  Password: admin123",
            font=UIStyleHelper.FONT_SMALL,
            bg="#EEF2FF",
            fg=THEME_COLORS["primary_dark"],
            relief="solid",
            bd=1,
            padx=10,
            pady=8
        )
        hint_box.grid(row=9, column=0, sticky="ew")

        # Bind Enter key to submit
        self.username_entry.bind("<Return>", lambda e: self._handle_login())
        self.password_entry.bind("<Return>", lambda e: self._handle_login())

    def _on_role_change(self) -> None:
        """Adapt input fields based on role selected."""
        role = self.role_var.get()
        if role == "STUDENT":
            self.id_label.config(text="Member ID (e.g. MEM-001):")
            self.pwd_label.grid_remove()
            self.password_entry.grid_remove()
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, "MEM-001")
        else:
            self.id_label.config(text="Username:")
            self.pwd_label.grid()
            self.password_entry.grid()
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, "admin")
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, "admin123")
        self.error_label.config(text="")

    def _handle_login(self) -> None:
        """Validate input and trigger authentication."""
        role = self.role_var.get()
        user_input = self.username_entry.get().strip()

        if not user_input:
            self.error_label.config(text="Please enter your username or Member ID.")
            return

        if role == "LIBRARIAN":
            password = self.password_entry.get()
            if not password:
                self.error_label.config(text="Please enter your password.")
                return

            user = self.auth_service.login(user_input, password)
            if user:
                self.error_label.config(text="")
                self.on_login_success(user)
            else:
                self.error_label.config(text="Invalid username or password. Please try again.")
        else:
            # Student / Member Portal Login
            from database.repositories import MemberRepository
            m_repo = MemberRepository()
            member = m_repo.get_member_by_id(user_input)
            if member:
                self.error_label.config(text="")
                self.on_login_success(member)
            else:
                self.error_label.config(text=f"Member ID '{user_input}' not found in registry.")
