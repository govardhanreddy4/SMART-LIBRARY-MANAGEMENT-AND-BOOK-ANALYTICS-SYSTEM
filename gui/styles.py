"""GUI Styling and TTK Theme Configuration."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import THEME_COLORS


class UIStyleHelper:
    """Configures modern ttk styles, typography, and widget appearances."""

    FONT_FAMILY = "Segoe UI"
    FONT_TITLE = (FONT_FAMILY, 16, "bold")
    FONT_HEADER = (FONT_FAMILY, 12, "bold")
    FONT_SUBHEADER = (FONT_FAMILY, 10, "bold")
    FONT_BODY = (FONT_FAMILY, 10)
    FONT_SMALL = (FONT_FAMILY, 8)
    FONT_METRIC = (FONT_FAMILY, 20, "bold")

    @classmethod
    def apply_styles(cls, root: tk.Tk) -> ttk.Style:
        """Apply custom visual styling across all standard ttk widgets."""
        style = ttk.Style(root)
        
        # Use 'clam' as the base theme for consistent cross-platform coloring
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Global Frame background
        style.configure("TFrame", background=THEME_COLORS["content_bg"])
        style.configure("Card.TFrame", background=THEME_COLORS["card_bg"], relief="flat")
        style.configure("Sidebar.TFrame", background=THEME_COLORS["sidebar_bg"])

        # Label Styling
        style.configure(
            "TLabel",
            background=THEME_COLORS["content_bg"],
            foreground=THEME_COLORS["text_dark"],
            font=cls.FONT_BODY
        )
        style.configure(
            "Sidebar.TLabel",
            background=THEME_COLORS["sidebar_bg"],
            foreground=THEME_COLORS["text_light"],
            font=cls.FONT_BODY
        )
        style.configure(
            "SidebarTitle.TLabel",
            background=THEME_COLORS["sidebar_bg"],
            foreground="#FFFFFF",
            font=(cls.FONT_FAMILY, 12, "bold")
        )
        style.configure(
            "Header.TLabel",
            font=cls.FONT_HEADER,
            foreground=THEME_COLORS["text_dark"],
            background=THEME_COLORS["content_bg"]
        )
        style.configure(
            "CardMetric.TLabel",
            font=cls.FONT_METRIC,
            background=THEME_COLORS["card_bg"],
            foreground=THEME_COLORS["primary"]
        )
        style.configure(
            "CardTitle.TLabel",
            font=cls.FONT_SMALL,
            background=THEME_COLORS["card_bg"],
            foreground=THEME_COLORS["text_muted"]
        )

        # Button Styling
        style.configure(
            "TButton",
            font=cls.FONT_BODY,
            padding=6,
            relief="flat",
            background=THEME_COLORS["primary"],
            foreground="#FFFFFF"
        )
        style.map(
            "TButton",
            background=[("active", THEME_COLORS["primary_dark"]), ("disabled", "#CBD5E1")],
            foreground=[("disabled", "#94A3B8")]
        )

        style.configure(
            "Success.TButton",
            background=THEME_COLORS["success"],
            foreground="#FFFFFF",
            font=cls.FONT_BODY,
            padding=6
        )
        style.map(
            "Success.TButton",
            background=[("active", "#059669")]
        )

        style.configure(
            "Danger.TButton",
            background=THEME_COLORS["danger"],
            foreground="#FFFFFF",
            font=cls.FONT_BODY,
            padding=6
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#DC2626")]
        )

        style.configure(
            "Nav.TButton",
            font=(cls.FONT_FAMILY, 10, "bold"),
            padding=10,
            background=THEME_COLORS["sidebar_bg"],
            foreground=THEME_COLORS["text_light"],
            anchor="w"
        )
        style.map(
            "Nav.TButton",
            background=[("active", THEME_COLORS["primary"]), ("selected", THEME_COLORS["primary"])]
        )

        # Treeview (Data Table) Styling
        style.configure(
            "Treeview",
            font=cls.FONT_BODY,
            rowheight=28,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground=THEME_COLORS["text_dark"]
        )
        style.configure(
            "Treeview.Heading",
            font=cls.FONT_SUBHEADER,
            background="#F1F5F9",
            foreground=THEME_COLORS["text_dark"],
            padding=6
        )
        style.map(
            "Treeview",
            background=[("selected", THEME_COLORS["primary_light"])],
            foreground=[("selected", "#FFFFFF")]
        )

        # Entry and Combobox
        style.configure("TEntry", padding=6)
        style.configure("TCombobox", padding=5)

        return style
