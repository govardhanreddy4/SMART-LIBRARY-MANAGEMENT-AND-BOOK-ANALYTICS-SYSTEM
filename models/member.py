"""Member model inheriting from Person demonstrating Inheritance and Method Overriding."""

from datetime import datetime
from typing import Dict, Any, List
from .person import Person


class Member(Person):
    """Represents a registered library borrower / student.
    
    Demonstrates:
    - Module I: Inheritance from base class Person
    - Module I: Method Overriding (get_role_display, get_permissions)
    - Module I: Polymorphism
    """

    def __init__(
        self,
        member_id: str,
        name: str,
        email: str,
        phone: str,
        created_at: str = None
    ):
        super().__init__(
            person_id=member_id,
            name=name,
            email=email,
            phone=phone,
            role="MEMBER"
        )
        self.member_id = self.person_id
        self.created_at = created_at or datetime.now().isoformat()

    # Module I: Method Overriding (Polymorphism)
    def get_role_display(self) -> str:
        """Override base display."""
        return "Library Member / Student"

    # Module I: Method Overriding (Polymorphism)
    def get_permissions(self) -> List[str]:
        """Override base permissions."""
        return ["VIEW_CATALOG", "BORROW_BOOK", "VIEW_OWN_LOANS"]

    @classmethod
    def from_row(cls, row: Any) -> "Member":
        """Instantiate Member from sqlite3 row dict or sqlite3.Row."""
        keys = row.keys() if hasattr(row, "keys") else row
        created = str(row["created_at"]) if "created_at" in keys else datetime.now().isoformat()
        return cls(
            member_id=str(row["member_id"]),
            name=str(row["name"]),
            email=str(row["email"]),
            phone=str(row["phone"]),
            created_at=created
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Member to dictionary."""
        d = super().to_dict()
        d["member_id"] = self.member_id
        d["created_at"] = self.created_at
        return d

    def __repr__(self) -> str:
        return f"Member(id={self.member_id!r}, name={self.name!r}, email={self.email!r})"
