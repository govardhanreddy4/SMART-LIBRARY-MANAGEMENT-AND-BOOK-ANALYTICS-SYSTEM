"""Librarian model inheriting from Person demonstrating Role Encapsulation and Password Hashing."""

import hashlib
import os
import secrets
from typing import Dict, Any, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import HASH_ALGORITHM, HASH_ITERATIONS, PASSWORD_SALT_LENGTH
from .person import Person


class Librarian(Person):
    """Represents an administrative staff member / librarian.
    
    Demonstrates:
    - Module I: Inheritance from Person
    - Module I: Method Overriding (get_role_display, get_permissions)
    - Module I: Encapsulation (protected hash & salt, no plaintext passwords)
    - Module I: Polymorphism
    """

    def __init__(
        self,
        librarian_id: str,
        name: str,
        email: str,
        phone: str,
        username: str,
        password_hash: str,
        salt: str,
        is_admin: bool = True
    ):
        super().__init__(
            person_id=librarian_id,
            name=name,
            email=email,
            phone=phone,
            role="LIBRARIAN"
        )
        self.librarian_id = self.person_id
        self.username = str(username).strip().lower()
        self._password_hash = password_hash
        self._salt = salt
        self.is_admin = bool(is_admin)

    @property
    def password_hash(self) -> str:
        """Read-only access to password hash."""
        return self._password_hash

    @property
    def salt(self) -> str:
        """Read-only access to password salt."""
        return self._salt

    # Module I: Method Overriding (Polymorphism)
    def get_role_display(self) -> str:
        """Return human-readable role."""
        return "Chief Librarian (Administrator)" if self.is_admin else "Assistant Librarian"

    # Module I: Method Overriding (Polymorphism)
    def get_permissions(self) -> List[str]:
        """Return admin permissions."""
        return [
            "VIEW_CATALOG",
            "MANAGE_BOOKS",
            "MANAGE_MEMBERS",
            "ISSUE_BOOK",
            "RETURN_BOOK",
            "VIEW_ANALYTICS",
            "EXPORT_DATA",
            "API_IMPORT"
        ]

    def verify_password(self, password: str) -> bool:
        """Verify candidate plaintext password using PBKDF2-HMAC."""
        if not password or not self._salt or not self._password_hash:
            return False
        
        salt_bytes = bytes.fromhex(self._salt)
        calc_hash = hashlib.pbkdf2_hmac(
            HASH_ALGORITHM,
            password.encode("utf-8"),
            salt_bytes,
            HASH_ITERATIONS
        ).hex()
        return secrets.compare_digest(calc_hash, self._password_hash)

    @classmethod
    def hash_password(cls, password: str) -> tuple[str, str]:
        """Generate a random salt and PBKDF2 hash for a password.
        
        Demonstrates Class Method for cryptographic credential generation.
        """
        salt_bytes = os.urandom(PASSWORD_SALT_LENGTH)
        pwd_hash = hashlib.pbkdf2_hmac(
            HASH_ALGORITHM,
            password.encode("utf-8"),
            salt_bytes,
            HASH_ITERATIONS
        ).hex()
        return pwd_hash, salt_bytes.hex()

    @classmethod
    def from_row(cls, row: Any) -> "Librarian":
        """Instantiate Librarian from database record or sqlite3.Row."""
        keys = row.keys() if hasattr(row, "keys") else row
        admin_flag = bool(row["is_admin"]) if "is_admin" in keys else True
        return cls(
            librarian_id=str(row["librarian_id"]),
            name=str(row["name"]),
            email=str(row["email"]),
            phone=str(row["phone"]),
            username=str(row["username"]),
            password_hash=str(row["password_hash"]),
            salt=str(row["salt"]),
            is_admin=admin_flag
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Librarian to dict (excluding sensitive password hash)."""
        d = super().to_dict()
        d["librarian_id"] = self.librarian_id
        d["username"] = self.username
        d["is_admin"] = self.is_admin
        return d
