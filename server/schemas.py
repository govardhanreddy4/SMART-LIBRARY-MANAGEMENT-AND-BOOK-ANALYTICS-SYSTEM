"""Pydantic Request and Response Schemas for FastAPI REST API."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class LibrarianRegisterRequest(BaseModel):
    librarian_id: str = Field(..., min_length=2)
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)
    email: str = Field(...)
    phone: str = Field(...)
    is_admin: bool = False


class BookCreate(BaseModel):
    book_id: str = Field(..., min_length=1, description="Unique Book ID (e.g., BK-1001)")
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    price: float = Field(..., ge=0.0)
    total_copies: int = Field(..., ge=1)
    available_copies: Optional[int] = Field(None, ge=0)


class BookUpdate(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    price: float = Field(..., ge=0.0)
    total_copies: int = Field(..., ge=1)
    available_copies: int = Field(..., ge=0)


class MemberCreate(BaseModel):
    member_id: str = Field(..., min_length=1, description="Unique Member ID (e.g., MEM-001)")
    name: str = Field(..., min_length=2)
    email: str = Field(...)
    phone: str = Field(...)


class MemberUpdate(BaseModel):
    name: str = Field(..., min_length=2)
    email: str = Field(...)
    phone: str = Field(...)


class LoanIssueRequest(BaseModel):
    book_id: str = Field(..., min_length=1)
    member_id: str = Field(..., min_length=1)
    loan_days: int = Field(14, ge=1, le=90)


class LoanReturnRequest(BaseModel):
    return_date: Optional[str] = None


class GoogleBookImportRequest(BaseModel):
    book_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    price: float = Field(..., ge=0.0)
    total_copies: int = Field(..., ge=1)


class BenchmarkRequest(BaseModel):
    total_simulations: int = Field(100_000, ge=10_000, le=2_000_000)
    num_chunks: int = Field(8, ge=2, le=32)
