"""Data Visualization generators using Matplotlib for Tkinter embedding."""

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional, Tuple
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from analytics.data_processor import DataProcessor
from services.report_service import ReportService
from config import THEME_COLORS
from utils.logging_config import get_logger

logger = get_logger("analytics.visualizations")


class ChartGenerator:
    """Generates styled Matplotlib figures for embedding in Tkinter GUI.
    
    Demonstrates:
    - Module IV: Matplotlib data visualization
    - Bar charts, donut charts, and trend line charts
    - Graceful empty-dataset handling
    """

    def __init__(self, db_path: Optional[str] = None):
        self.processor = DataProcessor(db_path)
        self.report_service = ReportService(db_path)

    def create_category_bar_chart(self, figsize: Tuple[int, int] = (6, 4)) -> Figure:
        """Chart 1: Bar chart comparing Total vs Available copies by category."""
        fig = Figure(figsize=figsize, dpi=100, facecolor="#F8FAFC")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#FFFFFF")

        cat_df = self.processor.get_category_analytics()

        if cat_df.empty or len(cat_df) == 0:
            ax.text(0.5, 0.5, "No Category Data Available", ha="center", va="center", color="#64748B", fontsize=12)
            ax.set_axis_off()
            fig.tight_layout()
            return fig

        categories = cat_df["category"].tolist()
        total_copies = cat_df["total_copies"].tolist()
        avail_copies = cat_df["available_copies"].tolist()

        x = range(len(categories))
        width = 0.35

        ax.bar([i - width/2 for i in x], total_copies, width=width, label="Total Copies", color=THEME_COLORS["primary"], alpha=0.9)
        ax.bar([i + width/2 for i in x], avail_copies, width=width, label="Available", color=THEME_COLORS["success"], alpha=0.9)

        ax.set_title("Book Inventory by Category", fontsize=12, fontweight="bold", pad=12, color=THEME_COLORS["text_dark"])
        ax.set_xlabel("Category", fontsize=10, fontweight="bold", labelpad=8, color=THEME_COLORS["text_dark"])
        ax.set_ylabel("Quantity", fontsize=10, fontweight="bold", labelpad=8, color=THEME_COLORS["text_dark"])
        ax.set_xticks(list(x))
        ax.set_xticklabels(categories, rotation=25, ha="right", fontsize=9)
        ax.legend(frameon=True, facecolor="#FFFFFF", edgecolor=THEME_COLORS["border"])
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        fig.tight_layout()
        return fig

    def create_circulation_status_donut_chart(self, figsize: Tuple[int, int] = (5, 4)) -> Figure:
        """Chart 2: Donut chart displaying mutually exclusive inventory and loan segments.
        
        Definitions used:
        - Available on Shelf: Available copies currently in library.
        - Issued (On-Time): Active loans where due date has not passed.
        - Issued (Overdue): Active loans where due date has passed.
        These three segments sum to total physical inventory without double-counting.
        """
        fig = Figure(figsize=figsize, dpi=100, facecolor="#F8FAFC")
        ax = fig.add_subplot(111)

        summary = self.report_service.get_dashboard_summary()
        available = summary["available_copies"]
        overdue = summary["overdue_loans"]
        # On-time issued = total issued - overdue
        on_time = max(0, summary["issued_copies"] - overdue)

        values = [available, on_time, overdue]
        labels = [f"Available ({available})", f"On-Time Loans ({on_time})", f"Overdue Loans ({overdue})"]
        colors = [THEME_COLORS["success"], THEME_COLORS["secondary"], THEME_COLORS["danger"]]

        total = sum(values)
        if total == 0:
            ax.text(0.5, 0.5, "No Circulation Records", ha="center", va="center", color="#64748B", fontsize=12)
            ax.set_axis_off()
            fig.tight_layout()
            return fig

        # Filter out 0 segments for clean rendering
        filtered_vals = []
        filtered_labels = []
        filtered_colors = []
        for v, l, c in zip(values, labels, colors):
            if v > 0:
                filtered_vals.append(v)
                filtered_labels.append(l)
                filtered_colors.append(c)

        wedges, texts, autotexts = ax.pie(
            filtered_vals,
            labels=filtered_labels,
            colors=filtered_colors,
            autopct="%1.1f%%",
            startangle=140,
            pctdistance=0.75,
            textprops={"fontsize": 9, "color": THEME_COLORS["text_dark"]}
        )
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_weight("bold")

        # Create donut hole
        centre_circle = plt.Circle((0, 0), 0.55, fc="#F8FAFC")
        ax.add_artist(centre_circle)

        ax.set_title("Inventory & Circulation Breakdown", fontsize=12, fontweight="bold", pad=12, color=THEME_COLORS["text_dark"])
        fig.tight_layout()
        return fig

    def create_popular_books_chart(self, figsize: Tuple[int, int] = (6, 4)) -> Figure:
        """Chart 3: Horizontal bar chart showing most borrowed books."""
        fig = Figure(figsize=figsize, dpi=100, facecolor="#F8FAFC")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#FFFFFF")

        pop_df = self.processor.get_most_borrowed_books(top_n=5)
        if pop_df.empty or len(pop_df) == 0:
            ax.text(0.5, 0.5, "No Borrowing History Available", ha="center", va="center", color="#64748B", fontsize=12)
            ax.set_axis_off()
            fig.tight_layout()
            return fig

        # Truncate titles if long for clean axis
        titles = [t[:25] + "..." if len(t) > 25 else t for t in pop_df["title"].tolist()]
        counts = pop_df["loan_count"].tolist()

        y = range(len(titles))
        ax.barh(list(y), counts, color=THEME_COLORS["primary_light"], edgecolor=THEME_COLORS["primary"])
        ax.set_yticks(list(y))
        ax.set_yticklabels(titles, fontsize=9)
        ax.invert_yaxis()  # Top book on top
        ax.set_title("Top 5 Most Borrowed Books", fontsize=12, fontweight="bold", pad=12, color=THEME_COLORS["text_dark"])
        ax.set_xlabel("Number of Times Borrowed", fontsize=10, fontweight="bold", labelpad=8, color=THEME_COLORS["text_dark"])
        ax.grid(axis="x", linestyle="--", alpha=0.4)

        fig.tight_layout()
        return fig
