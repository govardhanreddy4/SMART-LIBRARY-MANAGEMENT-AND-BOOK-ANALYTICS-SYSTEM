"""Advanced Data Analytics Router powered by Pandas and NumPy."""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List

from server.dependencies import get_data_processor
from analytics.data_processor import DataProcessor

router = APIRouter(prefix="/api/analytics", tags=["Analytics (Pandas & NumPy)"])


@router.get("/category-breakdown")
def get_category_analytics(processor: DataProcessor = Depends(get_data_processor)) -> List[Dict[str, Any]]:
    """Pandas DataFrame aggregation grouped by category with inventory valuations."""
    df = processor.get_category_analytics()
    return df.to_dict(orient="records")


@router.get("/price-stats")
def get_price_statistics(processor: DataProcessor = Depends(get_data_processor)) -> Dict[str, float]:
    """NumPy statistical measures of book prices (mean, median, std, min, max, percentiles)."""
    return processor.calculate_price_statistics_numpy()


@router.get("/loan-duration-stats")
def get_loan_duration_statistics(processor: DataProcessor = Depends(get_data_processor)) -> Dict[str, float]:
    """NumPy statistical metrics of circulation loan durations."""
    return processor.calculate_loan_duration_statistics_numpy()


@router.get("/popular-books")
def get_popular_books(top_n: int = 10, processor: DataProcessor = Depends(get_data_processor)) -> List[Dict[str, Any]]:
    """Pandas ranking of the most frequently borrowed books."""
    df = processor.get_most_borrowed_books(top_n=top_n)
    return df.to_dict(orient="records")


@router.get("/monthly-trends")
def get_monthly_trends(processor: DataProcessor = Depends(get_data_processor)) -> List[Dict[str, Any]]:
    """Pandas time-series aggregation of borrowing activity by month."""
    df = processor.get_monthly_borrowing_trends()
    return df.to_dict(orient="records")
