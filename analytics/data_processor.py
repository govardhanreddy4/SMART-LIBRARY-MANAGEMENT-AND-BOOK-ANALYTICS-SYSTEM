"""Data Analytics Processor utilizing Pandas and NumPy for operational intelligence."""

import pandas as pd
import numpy as np
from datetime import date, datetime
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.connection import get_connection
from utils.logging_config import get_logger

logger = get_logger("analytics.data_processor")


class DataProcessor:
    """Performs statistical computations and data transformations using Pandas and NumPy.
    
    Demonstrates:
    - Module IV: Pandas DataFrame aggregation, grouping, filtering, and merging
    - Module IV: NumPy numerical statistics (mean, median, standard deviation, percentiles)
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def load_books_dataframe(self) -> pd.DataFrame:
        """Load books catalog from SQLite into a Pandas DataFrame."""
        conn = get_connection(self.db_path)
        try:
            query = "SELECT book_id, title, author, category, price, total_copies, available_copies FROM books;"
            df = pd.read_sql_query(query, conn)
            # Ensure correct data types
            if not df.empty:
                df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
                df["total_copies"] = pd.to_numeric(df["total_copies"], errors="coerce").fillna(0).astype(int)
                df["available_copies"] = pd.to_numeric(df["available_copies"], errors="coerce").fillna(0).astype(int)
                df["issued_copies"] = df["total_copies"] - df["available_copies"]
            return df
        finally:
            conn.close()

    def load_loans_dataframe(self) -> pd.DataFrame:
        """Load circulation loans joined with book metadata into a Pandas DataFrame."""
        conn = get_connection(self.db_path)
        try:
            query = """
            SELECT l.loan_id, l.book_id, b.title, b.category, l.member_id, m.name as member_name,
                   l.issue_date, l.due_date, l.return_date, l.status
            FROM loans l
            LEFT JOIN books b ON l.book_id = b.book_id
            LEFT JOIN members m ON l.member_id = m.member_id;
            """
            df = pd.read_sql_query(query, conn)
            if not df.empty:
                df["issue_date"] = pd.to_datetime(df["issue_date"], errors="coerce")
                df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")
                df["return_date"] = pd.to_datetime(df["return_date"], errors="coerce")
            return df
        finally:
            conn.close()

    def get_category_analytics(self) -> pd.DataFrame:
        """Aggregate book counts, copies, and total monetary valuation by category using Pandas."""
        df = self.load_books_dataframe()
        if df.empty:
            return pd.DataFrame(columns=["category", "title_count", "total_copies", "available_copies", "issued_copies", "valuation"])

        # Compute row-level valuation
        df["valuation"] = df["price"] * df["total_copies"]

        # GroupBy and aggregation in Pandas
        agg_df = df.groupby("category").agg(
            title_count=("book_id", "count"),
            total_copies=("total_copies", "sum"),
            available_copies=("available_copies", "sum"),
            issued_copies=("issued_copies", "sum"),
            avg_price=("price", "mean"),
            valuation=("valuation", "sum")
        ).reset_index()

        return agg_df.sort_values(by="total_copies", ascending=False)

    def calculate_price_statistics_numpy(self) -> Dict[str, float]:
        """Compute comprehensive numerical statistics of book prices using NumPy.
        
        Demonstrates:
        - Module IV: NumPy array operations, mean, median, std, percentiles
        """
        df = self.load_books_dataframe()
        if df.empty or len(df) == 0:
            return {
                "count": 0, "mean": 0.0, "median": 0.0, "std": 0.0,
                "min": 0.0, "max": 0.0, "p25": 0.0, "p75": 0.0
            }

        prices = df["price"].to_numpy(dtype=float)
        
        # NumPy statistical functions
        return {
            "count": int(prices.size),
            "mean": round(float(np.mean(prices)), 2),
            "median": round(float(np.median(prices)), 2),
            "std": round(float(np.std(prices)), 2),
            "min": round(float(np.min(prices)), 2),
            "max": round(float(np.max(prices)), 2),
            "p25": round(float(np.percentile(prices, 25)), 2),
            "p75": round(float(np.percentile(prices, 75)), 2)
        }

    def calculate_loan_duration_statistics_numpy(self) -> Dict[str, float]:
        """Compute statistics of loan durations (in days) using NumPy."""
        df = self.load_loans_dataframe()
        if df.empty:
            return {"count": 0, "mean_days": 0.0, "median_days": 0.0, "max_days": 0.0}

        # Calculate duration for completed loans
        completed = df.dropna(subset=["issue_date", "return_date"]).copy()
        if completed.empty:
            return {"count": 0, "mean_days": 0.0, "median_days": 0.0, "max_days": 0.0}

        durations = (completed["return_date"] - completed["issue_date"]).dt.days.to_numpy(dtype=float)
        # Ensure non-negative
        durations = np.maximum(durations, 0.0)

        return {
            "count": int(durations.size),
            "mean_days": round(float(np.mean(durations)), 1),
            "median_days": round(float(np.median(durations)), 1),
            "max_days": round(float(np.max(durations)), 1)
        }

    def get_most_borrowed_books(self, top_n: int = 5) -> pd.DataFrame:
        """Find the most frequently borrowed books using Pandas."""
        loans_df = self.load_loans_dataframe()
        if loans_df.empty:
            return pd.DataFrame(columns=["book_id", "title", "category", "loan_count"])

        counts = loans_df.groupby(["book_id", "title", "category"]).size().reset_index(name="loan_count")
        return counts.sort_values(by="loan_count", ascending=False).head(top_n)

    def get_monthly_borrowing_trends(self) -> pd.DataFrame:
        """Aggregate borrowing activity by Month-Year using Pandas."""
        loans_df = self.load_loans_dataframe()
        if loans_df.empty or loans_df["issue_date"].dropna().empty:
            return pd.DataFrame(columns=["period", "loan_count"])

        valid = loans_df.dropna(subset=["issue_date"]).copy()
        valid["period"] = valid["issue_date"].dt.strftime("%Y-%m")
        trends = valid.groupby("period").size().reset_index(name="loan_count")
        return trends.sort_values(by="period")
