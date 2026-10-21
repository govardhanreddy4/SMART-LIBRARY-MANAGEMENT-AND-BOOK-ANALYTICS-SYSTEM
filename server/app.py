"""FastAPI Application Main Entry Point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.routers import (
    auth,
    dashboard,
    books,
    members,
    loans,
    analytics,
    google_books,
    concurrency,
    reports
)

app = FastAPI(
    title="Smart Library Management and Book Analytics System REST API",
    description="High-performance REST API backend powering React frontend and analytical engines.",
    version="1.0.0"
)

# CORS configuration allowing local Vite development server and production builds
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)
app.include_router(analytics.router)
app.include_router(google_books.router)
app.include_router(concurrency.router)
app.include_router(reports.router)


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify backend operational readiness."""
    return {
        "status": "healthy",
        "service": "Smart Library Management REST API",
        "version": "1.0.0"
    }
