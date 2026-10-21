"""Member Service managing user registration and safe lifecycle."""

from typing import List, Optional, Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.repositories import MemberRepository
from models.member import Member
from utils.validators import Validators
from utils.file_handlers import DataExporter
from utils.logging_config import get_logger

logger = get_logger("services.member_service")


class MemberService:
    """Service providing member management and registration verification."""

    def __init__(self, member_repo: Optional[MemberRepository] = None):
        self.repo = member_repo or MemberRepository()

    def register_member(self, member_id: str, name: str, email: str, phone: str) -> Member:
        """Register a new library member with regex validation."""
        ok, err = Validators.validate_member_inputs(member_id, name, email, phone)
        if not ok:
            raise ValueError(err)

        existing = self.repo.get_member_by_id(member_id)
        if existing:
            raise ValueError(f"Member with ID '{member_id}' already registered.")

        member = Member(member_id=member_id, name=name, email=email, phone=phone)
        self.repo.add_member(member)
        return member

    def get_member(self, member_id: str) -> Optional[Member]:
        """Fetch member by ID."""
        return self.repo.get_member_by_id(member_id)

    def get_all_members(self) -> List[Member]:
        """Retrieve all registered members."""
        return self.repo.get_all_members()

    def update_member(self, member_id: str, name: str, email: str, phone: str) -> Member:
        """Update existing member contact details."""
        ok, err = Validators.validate_member_inputs(member_id, name, email, phone)
        if not ok:
            raise ValueError(err)

        existing = self.repo.get_member_by_id(member_id)
        if not existing:
            raise ValueError(f"Member '{member_id}' not found.")

        member = Member(
            member_id=member_id,
            name=name,
            email=email,
            phone=phone,
            created_at=existing.created_at
        )
        self.repo.update_member(member)
        return member

    def delete_member(self, member_id: str) -> bool:
        """Safely delete member if no active loans or history exist."""
        return self.repo.delete_member(member_id)

    def search_members(self, query: str = "") -> List[Member]:
        """Search members by keyword."""
        return self.repo.search_members(query)

    def export_members(self, file_path: str, format_type: str = "CSV") -> bool:
        """Export member directory to CSV or JSON."""
        data = [m.to_dict() for m in self.get_all_members()]
        if format_type.upper() == "CSV":
            return DataExporter.export_to_csv(data, file_path)
        elif format_type.upper() == "JSON":
            return DataExporter.export_to_json(data, file_path)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
