"""Dashboard Summary and Metrics Router."""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List

from server.dependencies import get_report_service, get_loan_service
from services.report_service import ReportService
from services.loan_service import LoanService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_summary(report_service: ReportService = Depends(get_report_service)) -> Dict[str, Any]:
    """Get live key operational metrics calculated from SQLite."""
    return report_service.get_dashboard_summary()


@router.get("/charts")
def get_chart_data(
    report_service: ReportService = Depends(get_report_service),
    loan_service: LoanService = Depends(get_loan_service)
) -> Dict[str, Any]:
    """Get aggregated dataset for interactive Recharts visualizations."""
    summary = report_service.get_dashboard_summary()
    cat_breakdown = report_service.get_category_breakdown()
    popular = report_service.get_popular_books(limit=6)
    
    # Recent loans for activity timeline
    all_loans = loan_service.get_all_loans()
    # Sort by loan_id descending
    recent_loans = sorted(all_loans, key=lambda x: x.get("loan_id", 0), reverse=True)[:5]

    # Circulation status chart dataset
    circulation_status = [
        {"name": "Available on Shelves", "value": summary.get("available_copies", 0), "color": "#10B981"},
        {"name": "Active Loans", "value": max(0, summary.get("issued_copies", 0) - summary.get("overdue_loans", 0)), "color": "#4F46E5"},
        {"name": "Overdue Loans", "value": summary.get("overdue_loans", 0), "color": "#EF4444"}
    ]

    return {
        "summary": summary,
        "category_data": cat_breakdown,
        "circulation_status": circulation_status,
        "popular_books": popular,
        "recent_loans": recent_loans
    }
