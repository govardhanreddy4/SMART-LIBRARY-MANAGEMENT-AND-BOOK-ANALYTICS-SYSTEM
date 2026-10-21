"""Authentication and Authorization Router."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from server.schemas import LoginRequest, LibrarianRegisterRequest
from server.dependencies import get_auth_service
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login")
def login(creds: LoginRequest, auth: AuthService = Depends(get_auth_service)) -> Dict[str, Any]:
    """Authenticate librarian or student with credentials."""
    user = auth.login(creds.username, creds.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    return {
        "success": True,
        "message": f"Welcome back, {user.name}!",
        "user": {
            "id": user.librarian_id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "is_admin": user.is_admin,
            "role": user.get_role_display()
        }
    }


@router.post("/logout")
def logout(auth: AuthService = Depends(get_auth_service)) -> Dict[str, Any]:
    """Clear active user session."""
    auth.logout()
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
def get_current_user(auth: AuthService = Depends(get_auth_service)) -> Dict[str, Any]:
    """Get active authenticated user in current session."""
    user = auth.current_user
    if not user:
        # Default fallback to admin for ease of testing or unauthenticated indicator
        return {
            "authenticated": False,
            "user": None
        }
    return {
        "authenticated": True,
        "user": {
            "id": getattr(user, "librarian_id", getattr(user, "member_id", "ID")),
            "username": getattr(user, "username", user.name),
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "is_admin": getattr(user, "is_admin", False),
            "role": user.get_role_display()
        }
    }


@router.post("/register-librarian")
def register_librarian(req: LibrarianRegisterRequest, auth: AuthService = Depends(get_auth_service)) -> Dict[str, Any]:
    """Register a new librarian account (Admin only)."""
    try:
        success = auth.register_librarian(
            librarian_id=req.librarian_id,
            name=req.name,
            email=req.email,
            phone=req.phone,
            username=req.username,
            password=req.password,
            is_admin=req.is_admin
        )
        return {"success": success, "message": f"Librarian '{req.username}' created successfully."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
