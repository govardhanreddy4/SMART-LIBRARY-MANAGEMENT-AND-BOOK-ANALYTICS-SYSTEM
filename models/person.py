"""Base Person model demonstrating Encapsulation, Polymorphism, Class Methods, and Dunder Methods."""

from typing import Dict, Any, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.validators import Validators


class Person:
    """Base class representing a person in the library system.
    
    Demonstrates:
    - Module I: Classes and objects, constructors and initialization
    - Module I: Encapsulation (protected attributes with @property getters & setters)
    - Module I: Special/dunder methods (__str__, __repr__, __eq__)
    - Module I: Class method and Static method
    - Module I: Base class for Inheritance and Polymorphism
    """

    VALID_ROLES = {"LIBRARIAN", "MEMBER", "STUDENT"}

    def __init__(self, person_id: str, name: str, email: str, phone: str, role: str = "MEMBER"):
        self.person_id = str(person_id).strip()
        self.name = str(name).strip()
        self._email = ""
        self._phone = ""
        self.role = role.upper()

        # Use property setters for encapsulated validation
        self.email = email
        self.phone = phone

    # Encapsulation: Email property with validation
    @property
    def email(self) -> str:
        """Get encapsulated email address."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Set email with validation."""
        val = str(value).strip()
        if not Validators.is_valid_email(val):
            raise ValueError(f"Invalid email address: '{val}'")
        self._email = val

    # Encapsulation: Phone property with validation
    @property
    def phone(self) -> str:
        """Get encapsulated phone number."""
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        """Set phone with validation."""
        val = str(value).strip()
        if not Validators.is_valid_phone(val):
            raise ValueError(f"Invalid phone number: '{val}'")
        self._phone = val

    # Instance Method
    def get_contact_info(self) -> str:
        """Return formatted contact details."""
        return f"{self.name} | Email: {self.email} | Phone: {self.phone}"

    # Polymorphic methods to be overridden in subclasses
    def get_role_display(self) -> str:
        """Polymorphic method for role description."""
        return f"General Person ({self.role})"

    def get_permissions(self) -> List[str]:
        """Polymorphic method returning granted permissions."""
        return ["VIEW_CATALOG"]

    # Module I: Static Method
    @staticmethod
    def is_valid_role(role_name: str) -> bool:
        """Check if a given role name is supported."""
        return bool(role_name and role_name.upper() in Person.VALID_ROLES)

    # Module I: Class Method
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Person":
        """Instantiate Person object from a dictionary."""
        return cls(
            person_id=data["person_id"],
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            role=data.get("role", "MEMBER")
        )

    # Module I: Special / Dunder Methods
    def __str__(self) -> str:
        return f"{self.name} ({self.person_id}) - {self.get_role_display()}"

    def __repr__(self) -> str:
        return f"Person(id={self.person_id!r}, name={self.name!r}, role={self.role!r})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Person):
            return self.person_id == other.person_id
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary representation."""
        return {
            "person_id": self.person_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role
        }
