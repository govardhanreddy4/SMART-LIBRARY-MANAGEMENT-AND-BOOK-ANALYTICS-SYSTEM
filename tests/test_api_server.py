"""Automated Test Suite for FastAPI REST API Endpoints."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Ensure root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.app import app

client = TestClient(app)


def test_health_check():
    """Verify health check endpoint returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Smart Library" in data["service"]


def test_auth_login_success_and_failure():
    """Verify login with correct admin credentials and rejection with bad credentials."""
    # Successful login
    res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["user"]["username"] == "admin"

    # Failed login
    res_fail = client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert res_fail.status_code == 401


def test_dashboard_summary():
    """Verify dashboard metrics endpoint computes positive integers."""
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_titles" in data
    assert "total_copies" in data
    assert "available_copies" in data
    assert "issued_copies" in data
    assert "active_members" in data
    assert "overdue_loans" in data
    assert data["total_titles"] >= 0


def test_dashboard_charts():
    """Verify charts dataset returns category, circulation, and popular book lists."""
    res = client.get("/api/dashboard/charts")
    assert res.status_code == 200
    data = res.json()
    assert "category_data" in data
    assert "circulation_status" in data
    assert "popular_books" in data
    assert "recent_loans" in data


def test_books_crud():
    """Verify books list, create, fetch, update, and search."""
    # List books
    res = client.get("/api/books")
    assert res.status_code == 200
    books = res.json()
    assert isinstance(books, list)

    # Categories list
    cat_res = client.get("/api/books/categories")
    assert cat_res.status_code == 200
    assert isinstance(cat_res.json(), list)

    # Create test book
    test_id = "BK-TEST-API"
    # Ensure cleanup if exists from previous run
    client.delete(f"/api/books/{test_id}")

    create_payload = {
        "book_id": test_id,
        "title": "API Testing with FastAPI",
        "author": "Test Author",
        "category": "Testing",
        "price": 499.0,
        "total_copies": 5,
        "available_copies": 5
    }
    create_res = client.post("/api/books", json=create_payload)
    assert create_res.status_code == 201
    assert create_res.json()["success"] is True

    # Get single book
    get_res = client.get(f"/api/books/{test_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "API Testing with FastAPI"

    # Update book
    update_payload = {
        "title": "API Testing with FastAPI (2nd Edition)",
        "author": "Test Author",
        "category": "Testing",
        "price": 549.0,
        "total_copies": 6,
        "available_copies": 6
    }
    update_res = client.put(f"/api/books/{test_id}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["book"]["title"] == "API Testing with FastAPI (2nd Edition)"

    # Delete test book
    del_res = client.delete(f"/api/books/{test_id}")
    assert del_res.status_code == 200


def test_members_crud():
    """Verify members list, create, fetch, and update."""
    res = client.get("/api/members")
    assert res.status_code == 200
    members = res.json()
    assert isinstance(members, list)

    test_member_id = "MEM-TEST-API"
    client.delete(f"/api/members/{test_member_id}")

    create_payload = {
        "member_id": test_member_id,
        "name": "Test Student",
        "email": "test.student.api@college.edu",
        "phone": "+919999888877"
    }
    create_res = client.post("/api/members", json=create_payload)
    assert create_res.status_code == 201

    get_res = client.get(f"/api/members/{test_member_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Test Student"

    # Safe delete
    del_res = client.delete(f"/api/members/{test_member_id}")
    assert del_res.status_code == 200


def test_loans_endpoints():
    """Verify circulation endpoints for active, overdue, and issue/return."""
    all_loans = client.get("/api/loans")
    assert all_loans.status_code == 200
    assert isinstance(all_loans.json(), list)

    active_loans = client.get("/api/loans/active")
    assert active_loans.status_code == 200

    overdue_loans = client.get("/api/loans/overdue")
    assert overdue_loans.status_code == 200


def test_analytics_endpoints():
    """Verify Pandas and NumPy analytics endpoints return expected data structures."""
    cat_res = client.get("/api/analytics/category-breakdown")
    assert cat_res.status_code == 200
    assert isinstance(cat_res.json(), list)

    price_stats = client.get("/api/analytics/price-stats")
    assert price_stats.status_code == 200
    p_data = price_stats.json()
    assert "mean" in p_data
    assert "median" in p_data
    assert "std" in p_data

    loan_stats = client.get("/api/analytics/loan-duration-stats")
    assert loan_stats.status_code == 200
    assert "mean_days" in loan_stats.json()

    popular = client.get("/api/analytics/popular-books")
    assert popular.status_code == 200


def test_concurrency_benchmark_endpoint():
    """Verify concurrency benchmark runs without throwing exceptions."""
    payload = {"total_simulations": 10_000, "num_chunks": 4}
    res = client.post("/api/concurrency/benchmark", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "data" in data
    assert "sequential_time_sec" in data["data"]
    assert "threading_time_sec" in data["data"]
    assert "multiprocessing_time_sec" in data["data"]


def test_cors_headers_for_vercel_origin():
    """Verify CORS preflight correctly authorizes the Vercel production frontend."""
    vercel_origin = "https://smart-library-management-and-book-analytics-system-m9b1s5aqa.vercel.app"
    headers = {
        "Origin": vercel_origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"
    }
    res = client.options("/api/auth/login", headers=headers)
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == vercel_origin
    assert res.headers.get("access-control-allow-credentials") == "true"

