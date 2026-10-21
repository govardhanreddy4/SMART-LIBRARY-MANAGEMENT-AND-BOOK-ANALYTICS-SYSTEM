"""Comprehensive Analytics View embedding Matplotlib charts and NumPy/Pandas metrics."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any, List
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from analytics.data_processor import DataProcessor
from analytics.visualizations import ChartGenerator
from services.report_service import ReportService
from config import THEME_COLORS
from gui.styles import UIStyleHelper
from utils.logging_config import get_logger

logger = get_logger("gui.analytics_view")


class AnalyticsView(ttk.Frame):
    """Deep-dive analytics dashboard displaying statistical breakdowns and embedded charts."""

    def __init__(self, parent: tk.Widget, db_path: Optional[str] = None):
        super().__init__(parent)
        self.db_path = db_path
        self.processor = DataProcessor(db_path)
        self.chart_gen = ChartGenerator(db_path)
        self.report_service = ReportService(db_path)

        self.configure(style="TFrame")
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header Frame
        hdr = tk.Frame(self, bg=THEME_COLORS["content_bg"])
        hdr.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        title = tk.Label(
            hdr,
            text="Library Data Analytics & Statistical Intelligence",
            font=UIStyleHelper.FONT_TITLE,
            bg=THEME_COLORS["content_bg"],
            fg=THEME_COLORS["text_dark"]
        )
        title.pack(side="left")

        act_frame = tk.Frame(hdr, bg=THEME_COLORS["content_bg"])
        act_frame.pack(side="right")

        ttk.Button(act_frame, text="🔄 Refresh Analytics", command=self.refresh_analytics).pack(side="left", padx=4)
        ttk.Button(act_frame, text="📤 Export Report", style="TButton", command=self._export_report).pack(side="left", padx=4)

        # Notebook tabs for 4 analytical perspectives
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=24, pady=(8, 20))

        self.tab_cat = ttk.Frame(self.notebook, style="TFrame")
        self.tab_donut = ttk.Frame(self.notebook, style="TFrame")
        self.tab_popular = ttk.Frame(self.notebook, style="TFrame")
        self.tab_stats = ttk.Frame(self.notebook, style="TFrame")

        self.notebook.add(self.tab_cat, text="📊 Category Inventory")
        self.notebook.add(self.tab_donut, text="🍩 Circulation Breakdown")
        self.notebook.add(self.tab_popular, text="⭐ Most Borrowed Books")
        self.notebook.add(self.tab_stats, text="📐 NumPy Price & Duration Statistics")

        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh_analytics())

        # Render first tab
        self._render_category_tab()

    def refresh_analytics(self) -> None:
        """Refresh active analytical tab."""
        tab_idx = self.notebook.index(self.notebook.select())
        if tab_idx == 0:
            self._render_category_tab()
        elif tab_idx == 1:
            self._render_circulation_tab()
        elif tab_idx == 2:
            self._render_popular_tab()
        elif tab_idx == 3:
            self._render_stats_tab()

    def _render_category_tab(self) -> None:
        for child in self.tab_cat.winfo_children():
            child.destroy()

        self.tab_cat.columnconfigure(0, weight=1)
        self.tab_cat.rowconfigure(1, weight=1)

        # Top chart frame
        chart_frame = tk.Frame(self.tab_cat, bg=THEME_COLORS["card_bg"], bd=1, relief="solid")
        chart_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=(12, 8))

        fig = self.chart_gen.create_category_bar_chart(figsize=(7, 3.2))
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

        # Bottom Pandas aggregated table
        table_frame = tk.Frame(self.tab_cat, bg=THEME_COLORS["card_bg"], bd=1, relief="solid")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 12))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        cols = ("category", "titles", "total_copies", "avail_copies", "issued_copies", "avg_price", "valuation")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=5)

        tree.heading("category", text="Category")
        tree.heading("titles", text="Distinct Titles")
        tree.heading("total_copies", text="Total Copies")
        tree.heading("avail_copies", text="Available")
        tree.heading("issued_copies", text="Issued")
        tree.heading("avg_price", text="Average Price (₹)")
        tree.heading("valuation", text="Category Valuation (₹)")

        tree.column("category", width=160, anchor="w")
        tree.column("titles", width=100, anchor="center")
        tree.column("total_copies", width=100, anchor="center")
        tree.column("avail_copies", width=100, anchor="center")
        tree.column("issued_copies", width=100, anchor="center")
        tree.column("avg_price", width=120, anchor="e")
        tree.column("valuation", width=140, anchor="e")

        tree.grid(row=0, column=0, sticky="nsew")

        # Load Pandas aggregated data
        df = self.processor.get_category_analytics()
        for _, row in df.iterrows():
            tree.insert(
                "", "end",
                values=(
                    row["category"],
                    int(row["title_count"]),
                    int(row["total_copies"]),
                    int(row["available_copies"]),
                    int(row["issued_copies"]),
                    f"{row['avg_price']:.2f}",
                    f"{row['valuation']:.2f}"
                )
            )

    def _render_circulation_tab(self) -> None:
        for child in self.tab_donut.winfo_children():
            child.destroy()

        self.tab_donut.columnconfigure(0, weight=1)
        self.tab_donut.rowconfigure(0, weight=1)

        chart_frame = tk.Frame(self.tab_donut, bg=THEME_COLORS["card_bg"], bd=1, relief="solid")
        chart_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        fig = self.chart_gen.create_circulation_status_donut_chart(figsize=(6, 4))
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def _render_popular_tab(self) -> None:
        for child in self.tab_popular.winfo_children():
            child.destroy()

        self.tab_popular.columnconfigure(0, weight=1)
        self.tab_popular.rowconfigure(0, weight=1)

        chart_frame = tk.Frame(self.tab_popular, bg=THEME_COLORS["card_bg"], bd=1, relief="solid")
        chart_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        fig = self.chart_gen.create_popular_books_chart(figsize=(6, 4))
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def _render_stats_tab(self) -> None:
        """Module IV: NumPy statistical distributions display."""
        for child in self.tab_stats.winfo_children():
            child.destroy()

        self.tab_stats.columnconfigure(0, weight=1)
        self.tab_stats.columnconfigure(1, weight=1)

        # Price Stats Card (NumPy)
        card1 = tk.Frame(self.tab_stats, bg=THEME_COLORS["card_bg"], bd=1, relief="solid", padx=20, pady=20)
        card1.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        tk.Label(
            card1,
            text="Book Catalog Price Statistics (NumPy)",
            font=UIStyleHelper.FONT_HEADER,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["primary"]
        ).pack(anchor="w", pady=(0, 14))

        p_stats = self.processor.calculate_price_statistics_numpy()
        stats_items = [
            ("Sample Size (N)", f"{p_stats['count']} books"),
            ("Mean Price (μ)", f"₹ {p_stats['mean']:.2f}"),
            ("Median Price (Q2)", f"₹ {p_stats['median']:.2f}"),
            ("Standard Deviation (σ)", f"₹ {p_stats['std']:.2f}"),
            ("Minimum Price", f"₹ {p_stats['min']:.2f}"),
            ("Maximum Price", f"₹ {p_stats['max']:.2f}"),
            ("25th Percentile (Q1)", f"₹ {p_stats['p25']:.2f}"),
            ("75th Percentile (Q3)", f"₹ {p_stats['p75']:.2f}"),
        ]

        for label_text, val_text in stats_items:
            row_f = tk.Frame(card1, bg=THEME_COLORS["card_bg"])
            row_f.pack(fill="x", pady=4)
            tk.Label(row_f, text=label_text, font=UIStyleHelper.FONT_BODY, bg=THEME_COLORS["card_bg"], fg=THEME_COLORS["text_dark"]).pack(side="left")
            tk.Label(row_f, text=val_text, font=UIStyleHelper.FONT_SUBHEADER, bg=THEME_COLORS["card_bg"], fg=THEME_COLORS["primary_dark"]).pack(side="right")

        # Loan Duration Stats Card (NumPy)
        card2 = tk.Frame(self.tab_stats, bg=THEME_COLORS["card_bg"], bd=1, relief="solid", padx=20, pady=20)
        card2.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)

        tk.Label(
            card2,
            text="Historical Loan Durations (NumPy)",
            font=UIStyleHelper.FONT_HEADER,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["secondary"]
        ).pack(anchor="w", pady=(0, 14))

        l_stats = self.processor.calculate_loan_duration_statistics_numpy()
        l_items = [
            ("Returned Loans Analyzed", f"{l_stats['count']} records"),
            ("Mean Borrowing Duration", f"{l_stats['mean_days']} days"),
            ("Median Borrowing Duration", f"{l_stats['median_days']} days"),
            ("Longest Loan Duration", f"{l_stats['max_days']} days"),
        ]

        for label_text, val_text in l_items:
            row_f = tk.Frame(card2, bg=THEME_COLORS["card_bg"])
            row_f.pack(fill="x", pady=4)
            tk.Label(row_f, text=label_text, font=UIStyleHelper.FONT_BODY, bg=THEME_COLORS["card_bg"], fg=THEME_COLORS["text_dark"]).pack(side="left")
            tk.Label(row_f, text=val_text, font=UIStyleHelper.FONT_SUBHEADER, bg=THEME_COLORS["card_bg"], fg=THEME_COLORS["secondary"]).pack(side="right")

    def _export_report(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Export Comprehensive Analytics Report",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("CSV Summary", "*.csv"), ("XML Report", "*.xml")]
        )
        if not file_path:
            return

        fmt = "CSV" if file_path.endswith(".csv") else ("XML" if file_path.endswith(".xml") else "JSON")
        try:
            self.report_service.export_summary_report(file_path, fmt)
            messagebox.showinfo("Export Success", f"Analytics report exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
