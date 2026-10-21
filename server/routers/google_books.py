"""Google Books REST API Integration Router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any

from server.schemas import GoogleBookImportRequest
from server.dependencies import get_google_books_api, get_book_service
from api.google_books import GoogleBooksAPI
from services.book_service import BookService

router = APIRouter(prefix="/api/google-books", tags=["Google Books API"])


@router.get("/search")
def search_google_books(
    q: str = Query(..., min_length=2, description="Search term for Google Books API"),
    api: GoogleBooksAPI = Depends(get_google_books_api)
) -> List[Dict[str, Any]]:
    """Query live Google Books REST API with fallback to local recommendations on offline/timeout."""
    try:
        results = api.search_books(query=q)
        return results
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Google Books API Error: {str(e)}")


@router.post("/import-catalog", status_code=status.HTTP_201_CREATED)
def import_to_catalog(
    payload: GoogleBookImportRequest,
    book_service: BookService = Depends(get_book_service)
) -> Dict[str, Any]:
    """Import a book discovered via Google Books API directly into the local SQLite inventory."""
    try:
        book = book_service.add_book(
            book_id=payload.book_id,
            title=payload.title,
            author=payload.author,
            category=payload.category,
            price=payload.price,
            total_copies=payload.total_copies,
            available_copies=payload.total_copies
        )
        return {
            "success": True,
            "message": f"Successfully imported '{book.title}' into library catalog.",
            "book": book.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
