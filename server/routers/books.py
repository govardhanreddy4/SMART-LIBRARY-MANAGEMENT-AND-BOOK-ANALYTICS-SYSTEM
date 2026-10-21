"""Books Management and Catalog Router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse, PlainTextResponse, Response
from typing import List, Dict, Any, Optional
import tempfile
import os

from server.schemas import BookCreate, BookUpdate
from server.dependencies import get_book_service
from services.book_service import BookService

router = APIRouter(prefix="/api/books", tags=["Books"])


@router.get("")
def list_books(
    query: str = Query("", description="Search term for title, author, or book_id"),
    category: str = Query("", description="Filter by category"),
    book_service: BookService = Depends(get_book_service)
) -> List[Dict[str, Any]]:
    """Retrieve catalog books with optional keyword search and category filtering."""
    books = book_service.search_books(query=query, category=category)
    return [b.to_dict() for b in books]


@router.get("/categories")
def get_categories(book_service: BookService = Depends(get_book_service)) -> List[str]:
    """Retrieve unique book categories currently in the catalog."""
    return book_service.get_categories()


@router.get("/functional-demo")
def get_functional_programming_demo(book_service: BookService = Depends(get_book_service)) -> Dict[str, Any]:
    """Exposes Module II functional programming operations (map, filter, reduce, comprehensions)."""
    books = book_service.get_all_books()
    return {
        "total_valuation_reduce": book_service.calculate_total_inventory_valuation(books),
        "available_books_count_filter": len(book_service.filter_available_books(books)),
        "formatted_summaries_map": book_service.format_book_summaries(books)[:5],
        "categories_set_comp": sorted(list(book_service.get_distinct_categories_set_comp(books))),
        "low_stock_titles_list_comp": book_service.get_low_stock_titles_list_comp(threshold=2)
    }


@router.get("/{book_id}")
def get_book(book_id: str, book_service: BookService = Depends(get_book_service)) -> Dict[str, Any]:
    """Fetch single book by ID."""
    book = book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book '{book_id}' not found.")
    return book.to_dict()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, book_service: BookService = Depends(get_book_service)) -> Dict[str, Any]:
    """Add a new book to the catalog with rigorous validation."""
    try:
        book = book_service.add_book(
            book_id=payload.book_id,
            title=payload.title,
            author=payload.author,
            category=payload.category,
            price=payload.price,
            total_copies=payload.total_copies,
            available_copies=payload.available_copies
        )
        return {"success": True, "message": f"Book '{book.title}' added successfully.", "book": book.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{book_id}")
def update_book(
    book_id: str,
    payload: BookUpdate,
    book_service: BookService = Depends(get_book_service)
) -> Dict[str, Any]:
    """Update details of an existing book."""
    try:
        book = book_service.update_book(
            book_id=book_id,
            title=payload.title,
            author=payload.author,
            category=payload.category,
            price=payload.price,
            total_copies=payload.total_copies,
            available_copies=payload.available_copies
        )
        return {"success": True, "message": f"Book '{book.title}' updated successfully.", "book": book.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{book_id}")
def delete_book(book_id: str, book_service: BookService = Depends(get_book_service)) -> Dict[str, Any]:
    """Safely delete book if no circulation history exists."""
    try:
        deleted = book_service.delete_book(book_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book '{book_id}' not found.")
        return {"success": True, "message": f"Book '{book_id}' removed from catalog."}
    except ValueError as e:
        # e.g., foreign key restriction or active loans
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/import")
async def import_books(
    file: UploadFile = File(...),
    book_service: BookService = Depends(get_book_service)
) -> Dict[str, Any]:
    """Upload and import books from a CSV or JSON file."""
    ext = file.filename.split(".")[-1].lower() if file.filename else "csv"
    if ext not in ("csv", "json"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV or JSON files are supported.")
    
    # Save uploaded file temporarily
    suffix = f".{ext}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        fmt = "CSV" if ext == "csv" else "JSON"
        result = book_service.import_catalog(tmp_path, format_type=fmt)
        return {
            "success": True,
            "message": f"Imported {result['imported']} books, skipped {result['skipped']}.",
            "details": result
        }
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.get("/export/{format_type}")
def export_books(format_type: str, book_service: BookService = Depends(get_book_service)):
    """Export catalog to CSV, JSON, or XML."""
    fmt = format_type.upper()
    if fmt not in ("CSV", "JSON", "XML"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supported formats: CSV, JSON, XML")

    suffix = f".{fmt.lower()}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name

    try:
        book_service.export_catalog(tmp_path, format_type=fmt)
        with open(tmp_path, "rb") as f:
            data = f.read()

        media_types = {
            "CSV": "text/csv",
            "JSON": "application/json",
            "XML": "application/xml"
        }
        return Response(
            content=data,
            media_type=media_types[fmt],
            headers={"Content-Disposition": f"attachment; filename=catalog_export.{fmt.lower()}"}
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
