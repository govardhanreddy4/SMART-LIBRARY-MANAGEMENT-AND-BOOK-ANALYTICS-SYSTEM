"""Members Management Router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from typing import List, Dict, Any, Optional
import tempfile
import os

from server.schemas import MemberCreate, MemberUpdate
from server.dependencies import get_member_service
from services.member_service import MemberService

router = APIRouter(prefix="/api/members", tags=["Members"])


@router.get("")
def list_members(
    query: str = Query("", description="Search term for name, ID, email, or phone"),
    member_service: MemberService = Depends(get_member_service)
) -> List[Dict[str, Any]]:
    """Retrieve members with optional keyword filtering."""
    members = member_service.search_members(query=query)
    return [m.to_dict() for m in members]


@router.get("/{member_id}")
def get_member(member_id: str, member_service: MemberService = Depends(get_member_service)) -> Dict[str, Any]:
    """Fetch single member by ID."""
    member = member_service.get_member(member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member '{member_id}' not found.")
    return member.to_dict()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreate, member_service: MemberService = Depends(get_member_service)) -> Dict[str, Any]:
    """Register a new member with regex validation for email and phone."""
    try:
        member = member_service.register_member(
            member_id=payload.member_id,
            name=payload.name,
            email=payload.email,
            phone=payload.phone
        )
        return {"success": True, "message": f"Member '{member.name}' registered successfully.", "member": member.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{member_id}")
def update_member(
    member_id: str,
    payload: MemberUpdate,
    member_service: MemberService = Depends(get_member_service)
) -> Dict[str, Any]:
    """Update contact information for an existing member."""
    try:
        member = member_service.update_member(
            member_id=member_id,
            name=payload.name,
            email=payload.email,
            phone=payload.phone
        )
        return {"success": True, "message": f"Member '{member.name}' updated successfully.", "member": member.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{member_id}")
def delete_member(member_id: str, member_service: MemberService = Depends(get_member_service)) -> Dict[str, Any]:
    """Safely delete member if no active loans or circulation history exist."""
    try:
        deleted = member_service.delete_member(member_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member '{member_id}' not found.")
        return {"success": True, "message": f"Member '{member_id}' removed from system."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/export/{format_type}")
def export_members(format_type: str, member_service: MemberService = Depends(get_member_service)):
    """Export member directory to CSV or JSON."""
    fmt = format_type.upper()
    if fmt not in ("CSV", "JSON"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supported formats: CSV, JSON")

    suffix = f".{fmt.lower()}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name

    try:
        member_service.export_members(tmp_path, format_type=fmt)
        with open(tmp_path, "rb") as f:
            data = f.read()

        media_types = {
            "CSV": "text/csv",
            "JSON": "application/json"
        }
        return Response(
            content=data,
            media_type=media_types[fmt],
            headers={"Content-Disposition": f"attachment; filename=members_export.{fmt.lower()}"}
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
