"""FastAPI Service Dependencies and Providers."""

from pathlib import Path
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.auth_service import AuthService
from services.book_service import BookService
from services.member_service import MemberService
from services.loan_service import LoanService
from services.report_service import ReportService
from analytics.data_processor import DataProcessor
from api.google_books import GoogleBooksAPI
from database.schema import init_db

# Guarantee database exists and is seeded
init_db()

_auth_service = AuthService()
_book_service = BookService()
_member_service = MemberService()
_loan_service = LoanService()
_report_service = ReportService()
_data_processor = DataProcessor()
_google_books_api = GoogleBooksAPI()


def get_auth_service() -> AuthService:
    return _auth_service


def get_book_service() -> BookService:
    return _book_service


def get_member_service() -> MemberService:
    return _member_service


def get_loan_service() -> LoanService:
    return _loan_service


def get_report_service() -> ReportService:
    return _report_service


def get_data_processor() -> DataProcessor:
    return _data_processor


def get_google_books_api() -> GoogleBooksAPI:
    return _google_books_api
