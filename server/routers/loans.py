"""Circulation and Loans Router."""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List, Dict, Any, Optional
import tempfile
import os

from server.schemas import LoanIssueRequest, LoanReturnRequest
from server.dependencies import get_loan_service
from services.loan_service import LoanService

router = APIRouter(prefix="/api/loans", tags=["Circulation & Loans"])


@router.get("")
def list_loans(loan_service: LoanService = Depends(get_loan_service)) -> List[Dict[str, Any]]:
    """Retrieve complete circulation history."""
    return loan_service.get_all_loans()


@router.get("/active")
def list_active_loans(loan_service: LoanService = Depends(get_loan_service)) -> List[Dict[str, Any]]:
    """Retrieve currently active (unreturned) loans."""
    return loan_service.get_active_loans()


@router.get("/overdue")
def list_overdue_loans(loan_service: LoanService = Depends(get_loan_service)) -> List[Dict[str, Any]]:
    """Retrieve active overdue loans with dynamically computed fines."""
    return loan_service.get_overdue_loans()


@router.post("/issue", status_code=status.HTTP_201_CREATED)
def issue_book(payload: LoanIssueRequest, loan_service: LoanService = Depends(get_loan_service)) -> Dict[str, Any]:
    """Issue a book to a member with stock and borrowing quota checks."""
    try:
        loan_id = loan_service.issue_book(
            book_id=payload.book_id,
            member_id=payload.member_id,
            loan_days=payload.loan_days
        )
        return {
            "success": True,
            "message": f"Book issued successfully. Loan ID: #{loan_id}",
            "loan_id": loan_id
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{loan_id}/return")
def return_book(
    loan_id: int,
    payload: Optional[LoanReturnRequest] = None,
    loan_service: LoanService = Depends(get_loan_service)
) -> Dict[str, Any]:
    """Process a book return, updating loan status and restocking inventory."""
    try:
        ret_date = payload.return_date if payload else None
        success = loan_service.return_book(loan_id=loan_id, return_date_str=ret_date)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to process return.")
        return {
            "success": True,
            "message": f"Loan #{loan_id} successfully marked returned."
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/export/{format_type}")
def export_loans(format_type: str, loan_service: LoanService = Depends(get_loan_service)):
    """Export loans history to CSV or JSON."""
    fmt = format_type.upper()
    if fmt not in ("CSV", "JSON"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supported formats: CSV, JSON")

    suffix = f".{fmt.lower()}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name

    try:
        loan_service.export_loans(tmp_path, format_type=fmt)
        with open(tmp_path, "rb") as f:
            data = f.read()

        media_types = {
            "CSV": "text/csv",
            "JSON": "application/json"
        }
        return Response(
            content=data,
            media_type=media_types[fmt],
            headers={"Content-Disposition": f"attachment; filename=circulation_loans.{fmt.lower()}"}
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
