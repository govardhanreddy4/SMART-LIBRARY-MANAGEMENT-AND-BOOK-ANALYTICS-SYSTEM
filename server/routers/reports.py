"""Reports and Export Router."""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import Dict, Any
import tempfile
import os

from server.dependencies import get_report_service
from services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/summary")
def get_report_summary(report_service: ReportService = Depends(get_report_service)) -> Dict[str, Any]:
    """Retrieve full operational report data structure."""
    return {
        "summary": report_service.get_dashboard_summary(),
        "categories": report_service.get_category_breakdown(),
        "popular_books": report_service.get_popular_books(10)
    }


@router.get("/download/{format_type}")
def download_summary_report(format_type: str, report_service: ReportService = Depends(get_report_service)):
    """Download full library summary report in CSV, JSON, or XML."""
    fmt = format_type.upper()
    if fmt not in ("CSV", "JSON", "XML"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supported formats: CSV, JSON, XML")

    suffix = f".{fmt.lower()}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name

    try:
        report_service.export_summary_report(tmp_path, format_type=fmt)
        with open(tmp_path, "rb") as f:
            data = f.read()

        media_types = {
            "CSV": "text/csv",
            "JSON": "application/json",
            "XML": "application/xml"
        }
        return Response(
            content=data,
            media_type=media_types[fmt],
            headers={"Content-Disposition": f"attachment; filename=library_report.{fmt.lower()}"}
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
