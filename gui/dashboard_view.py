"""Dashboard View featuring real-time statistical cards and embedded Matplotlib charts."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Optional
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from services.report_service import ReportService
from analytics.visualizations import ChartGenerator
from config import THEME_COLORS
from gui.styles import UIStyleHelper
from utils.logging_config import get_logger

logger = get_logger("gui.dashboard_view")


class DashboardView(ttk.Frame):
    """Operational overview displaying live inventory metrics and charts."""

    def __init__(
        self,
        parent: tk.Widget,
        report_service: ReportService,
        on_navigate: Optional[Callable[[str], None]] = None,
        db_path: Optional[str] = None
    ):
        super().__init__(parent)
        self.report_service = report_service
        self.on_navigate = on_navigate
        self.db_path = db_path
        self.chart_gen = ChartGenerator(db_path)

        self.card_labels: Dict[str, tk.Label] = {}
        self.canvases = []

        self._build_ui()
        self.refresh_dashboard()

    def _build_ui(self) -> None:
        """Construct top metrics cards and lower analytics chart layout."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Header Frame
        hdr_frame = tk.Frame(self, bg=THEME_COLORS["content_bg"])
        hdr_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        title_lbl = tk.Label(
            hdr_frame,
            text="Executive Library Dashboard",
            font=UIStyleHelper.FONT_TITLE,
            bg=THEME_COLORS["content_bg"],
            fg=THEME_COLORS["text_dark"]
        )
        title_lbl.pack(side="left")

        refresh_btn = ttk.Button(
            hdr_frame,
            text="🔄 Refresh Data",
            command=self.refresh_dashboard,
            style="TButton"
        )
        refresh_btn.pack(side="right")

        # 1. Metric Summary Cards Row
        cards_frame = tk.Frame(self, bg=THEME_COLORS["content_bg"])
        cards_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=10)

        # Configure 6 columns for the 6 required cards
        for col_idx in range(6):
            cards_frame.columnconfigure(col_idx, weight=1)

        metric_specs = [
            ("total_titles", "Book Titles", THEME_COLORS["primary"]),
            ("total_copies", "Total Copies", THEME_COLORS["secondary"]),
            ("available_copies", "On Shelves", THEME_COLORS["success"]),
            ("issued_copies", "Issued Copies", THEME_COLORS["warning"]),
            ("active_members", "Active Members", THEME_COLORS["primary_dark"]),
            ("overdue_loans", "Overdue Loans", THEME_COLORS["danger"]),
        ]

        for idx, (key, label_text, color) in enumerate(metric_specs):
            card = tk.Frame(cards_frame, bg=THEME_COLORS["card_bg"], relief="flat", bd=1, padx=12, pady=12)
            card.grid(row=0, column=idx, padx=6, sticky="ew")

            val_lbl = tk.Label(
                card,
                text="0",
                font=UIStyleHelper.FONT_METRIC,
                bg=THEME_COLORS["card_bg"],
                fg=color
            )
            val_lbl.pack(anchor="center")

            title_l = tk.Label(
                card,
                text=label_text,
                font=UIStyleHelper.FONT_SMALL,
                bg=THEME_COLORS["card_bg"],
                fg=THEME_COLORS["text_muted"]
            )
            title_l.pack(anchor="center")

            self.card_labels[key] = val_lbl

        # 2. Charts Container (Scrollable or 2-column layout)
        charts_container = tk.Frame(self, bg=THEME_COLORS["content_bg"])
        charts_container.grid(row=2, column=0, sticky="nsew", padx=24, pady=(10, 20))
        charts_container.columnconfigure(0, weight=3)
        charts_container.columnconfigure(1, weight=2)
        charts_container.rowconfigure(0, weight=1)

        # Left Chart: Category Bar Chart
        self.left_chart_frame = tk.Frame(charts_container, bg=THEME_COLORS["card_bg"], bd=1, relief="solid")
        self.left_chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Right Chart: Circulation Donut Chart
        self.right_chart_frame = tk.Frame(charts_container, bg=THEME_COLORS["card_bg"], bd=1, relief="solid")
        self.right_chart_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    def refresh_dashboard(self) -> None:
        """Fetch fresh figures from database and re-render visual charts."""
        try:
            summary = self.report_service.get_dashboard_summary()
            for key, lbl in self.card_labels.items():
                lbl.config(text=str(summary.get(key, 0)))

            self._render_charts()
            logger.info("Dashboard refreshed successfully.")
        except Exception as e:
            logger.error("Failed to refresh dashboard: %s", e, exc_info=True)

    def _render_charts(self) -> None:
        """Embed regenerated Matplotlib figures into Tkinter canvases."""
        # Clear existing canvases
        for child in self.left_chart_frame.winfo_children():
            child.destroy()
        for child in self.right_chart_frame.winfo_children():
            child.destroy()

        try:
            # 1. Category Bar Chart
            fig_cat = self.chart_gen.create_category_bar_chart(figsize=(6, 4))
            canvas_cat = FigureCanvasTkAgg(fig_cat, master=self.left_chart_frame)
            canvas_cat.draw()
            canvas_cat.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

            # 2. Circulation Donut Chart
            fig_circ = self.chart_gen.create_circulation_status_donut_chart(figsize=(5, 4))
            canvas_circ = FigureCanvasTkAgg(fig_circ, master=self.right_chart_frame)
            canvas_circ.draw()
            canvas_circ.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        except Exception as e:
            logger.error("Error drawing charts on dashboard: %s", e, exc_info=True)
