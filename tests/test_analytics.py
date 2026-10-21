"""Unit tests for Data Processor, NumPy calculations, and Matplotlib Visualizations."""

import pytest
import tempfile
from pathlib import Path
import sys
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.schema import init_db
from analytics.data_processor import DataProcessor
from analytics.visualizations import ChartGenerator
from services.report_service import ReportService


class TestAnalytics:
    """Test suite for Pandas aggregations, NumPy statistics, and Matplotlib figure generation."""

    @pytest.fixture
    def setup_data(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_path = f.name
        # Seed with initial sample records
        init_db(temp_path, seed_samples=True)
        processor = DataProcessor(temp_path)
        generator = ChartGenerator(temp_path)
        report_service = ReportService(temp_path)
        
        yield processor, generator, report_service, temp_path

        try:
            Path(temp_path).unlink(missing_ok=True)
        except Exception:
            pass

    def test_pandas_category_aggregation(self, setup_data):
        processor, _, _, _ = setup_data
        cat_df = processor.get_category_analytics()

        assert not cat_df.empty
        assert "category" in cat_df.columns
        assert "total_copies" in cat_df.columns
        assert "valuation" in cat_df.columns
        assert cat_df["total_copies"].sum() > 0

    def test_numpy_price_statistics(self, setup_data):
        processor, _, _, _ = setup_data
        stats = processor.calculate_price_statistics_numpy()

        assert stats["count"] == 10
        assert stats["mean"] > 0.0
        assert stats["median"] > 0.0
        assert stats["std"] > 0.0
        assert stats["min"] <= stats["median"] <= stats["max"]
        assert stats["p25"] <= stats["p75"]

    def test_dashboard_summary_definitions(self, setup_data):
        _, _, report_service, _ = setup_data
        summary = report_service.get_dashboard_summary()

        assert summary["total_titles"] == 10
        # Check conservation law: total_copies == available_copies + issued_copies
        assert summary["total_copies"] == summary["available_copies"] + summary["issued_copies"]
        assert summary["active_members"] == 5
        # Overdue loans is a subset of issued copies
        assert summary["overdue_loans"] <= summary["issued_copies"]

    def test_visualization_figures_generated(self, setup_data):
        _, generator, _, _ = setup_data

        # Test Bar Chart Figure
        fig1 = generator.create_category_bar_chart()
        assert fig1 is not None
        assert len(fig1.axes) > 0
        plt.close(fig1)

        # Test Donut Chart Figure
        fig2 = generator.create_circulation_status_donut_chart()
        assert fig2 is not None
        assert len(fig2.axes) > 0
        plt.close(fig2)

        # Test Popular Books Figure
        fig3 = generator.create_popular_books_chart()
        assert fig3 is not None
        assert len(fig3.axes) > 0
        plt.close(fig3)

    def test_empty_dataset_handling(self):
        """Verify analytics and charts handle empty tables gracefully."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_path = f.name
        init_db(temp_path, seed_samples=False)

        processor = DataProcessor(temp_path)
        generator = ChartGenerator(temp_path)

        stats = processor.calculate_price_statistics_numpy()
        assert stats["count"] == 0
        assert stats["mean"] == 0.0

        fig = generator.create_category_bar_chart()
        assert fig is not None
        plt.close(fig)

        try:
            Path(temp_path).unlink(missing_ok=True)
        except Exception:
            pass
