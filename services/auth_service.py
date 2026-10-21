"""Authentication Service with Role-Based Access Control and Decorator support."""

from functools import wraps
from typing import Optional, Callable, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.repositories import LibrarianRepository
from models.librarian import Librarian
from models.person import Person
from utils.logging_config import get_logger

logger = get_logger("services.auth_service")


# Module II: Custom Decorator for Role-Based Access Control
def require_librarian(func: Callable) -> Callable:
    """Decorator ensuring that only authenticated Librarians can execute protected methods.
    
    Demonstrates:
    - Module II: Python Decorator pattern with functools.wraps
    - Role-based authorization enforcement
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        # Check current user in service or context
        current_user = getattr(self, "current_user", None)
        if not current_user or not isinstance(current_user, Librarian):
            err_msg = f"Unauthorized: '{func.__name__}' requires Librarian administrative privileges."
            logger.warning(err_msg)
            raise PermissionError(err_msg)
        return func(self, *args, **kwargs)
    return wrapper


class AuthService:
    """Manages user authentication, session state, and credential validation."""

    def __init__(self, librarian_repo: Optional[LibrarianRepository] = None):
        self.repo = librarian_repo or LibrarianRepository()
        self._current_user: Optional[Person] = None

    @property
    def current_user(self) -> Optional[Person]:
        """Get currently authenticated user in session."""
        return self._current_user

    @property
    def is_authenticated(self) -> bool:
        """Check if an active session exists."""
        return self._current_user is not None

    @property
    def is_admin(self) -> bool:
        """Check if active user is an administrator."""
        return isinstance(self._current_user, Librarian) and self._current_user.is_admin

    def login(self, username: str, password: str) -> Optional[Librarian]:
        """Authenticate user with PBKDF2 hash comparison."""
        if not username or not password:
            logger.warning("Login failed: empty username or password.")
            return None

        librarian = self.repo.get_by_username(username.strip())
        if not librarian:
            logger.warning("Login failed: user '%s' not found.", username)
            return None

        if librarian.verify_password(password):
            self._current_user = librarian
            logger.info("User '%s' authenticated successfully (Role: %s)", username, librarian.get_role_display())
            return librarian

        logger.warning("Login failed: incorrect password for user '%s'.", username)
        return None

    def logout(self) -> None:
        """Clear active user session."""
        if self._current_user:
            logger.info("User '%s' logged out.", self._current_user.name)
        self._current_user = None

    def register_librarian(
        self,
        librarian_id: str,
        name: str,
        email: str,
        phone: str,
        username: str,
        password: str,
        is_admin: bool = False
    ) -> bool:
        """Create a new staff librarian account."""
        pwd_hash, salt = Librarian.hash_password(password)
        librarian = Librarian(
            librarian_id=librarian_id,
            name=name,
            email=email,
            phone=phone,
            username=username,
            password_hash=pwd_hash,
            salt=salt,
            is_admin=is_admin
        )
        return self.repo.add_librarian(librarian)
