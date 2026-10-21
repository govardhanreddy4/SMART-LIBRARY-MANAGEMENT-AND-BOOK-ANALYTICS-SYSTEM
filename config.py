"""Application Configuration for Smart Library Management and Book Analytics System."""

from pathlib import Path
import os

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DOCS_DIR = BASE_DIR / "docs"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DB_NAME = "library.db"
DB_PATH = DATA_DIR / DB_NAME
TEST_DB_PATH = DATA_DIR / "test_library.db"

# Security Configuration (PBKDF2-HMAC-SHA256)
PASSWORD_SALT_LENGTH = 16
HASH_ITERATIONS = 100_000
HASH_ALGORITHM = "sha256"

# Business Rules
DEFAULT_LOAN_DAYS = 14
DEFAULT_FINE_PER_DAY = 2.0  # ₹ or $ per overdue day
MAX_BOOKS_PER_MEMBER = 5

# REST API Configuration (Google Books)
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
API_TIMEOUT_SECONDS = 10
API_MAX_RESULTS = 20

# Concurrency & Performance Settings
THREAD_POOL_WORKERS = 4
MAX_ASYNC_CONCURRENT_REQUESTS = 5

# Logging Configuration
LOG_FILE_PATH = LOGS_DIR / "library_system.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] [%(threadName)s] %(message)s"
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB rotating
LOG_BACKUP_COUNT = 3

# UI Styling Constants
APP_TITLE = "Smart Library Management and Book Analytics System"
APP_VERSION = "1.0.0"
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 720

# UI Theme Color Palette (Modern Slate / Indigo Theme)
THEME_COLORS = {
    "primary": "#4F46E5",        # Indigo 600
    "primary_dark": "#4338CA",   # Indigo 700
    "primary_light": "#818CF8",  # Indigo 400
    "secondary": "#0EA5E9",      # Sky 500
    "success": "#10B981",        # Emerald 500
    "warning": "#F59E0B",        # Amber 500
    "danger": "#EF4444",         # Red 500
    "dark_bg": "#0F172A",        # Slate 900
    "sidebar_bg": "#1E293B",     # Slate 800
    "card_bg": "#FFFFFF",        # White
    "content_bg": "#F8FAFC",     # Slate 50
    "text_dark": "#0F172A",      # Slate 900
    "text_muted": "#64748B",     # Slate 500
    "text_light": "#F8FAFC",     # Slate 50
    "border": "#E2E8F0",         # Slate 200
}
