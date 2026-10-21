# Smart Library Management and Book Analytics System
### Advanced Python Programming — College Micro-Project (Academic Year 2026–2027)

A desktop library management application and analytical dashboard built with Python 3.11, Tkinter/ttk, SQLite, Pandas, NumPy, Matplotlib, and Google Books REST API.

---

## 🌟 Key Features

1. **Authentication & Role-Based Access Control**:
   - Secure login supporting **Librarian (Admin)** and **Student / Member** roles.
   - Salted `PBKDF2-HMAC-SHA256` password hashing (no plaintext passwords).
   - Parameterized SQL queries preventing SQL injection vulnerabilities.
   - Default Administrator Account: `admin` / `admin123`.

2. **Executive Real-Time Dashboard**:
   - 6 Live Summary Statistic Cards: Total Titles, Total Copies, Available on Shelf, Currently Issued, Active Members, and Overdue Loans.
   - Embedded Matplotlib Charts:
     - **Category Inventory Bar Chart** (Total vs Available physical stock).
     - **Circulation Breakdown Donut Chart** (Available on Shelf vs On-Time Active Loans vs Overdue Loans).

3. **Complete Book Inventory Management**:
   - Full CRUD: Add, Search, View, Edit, and Delete books.
   - Safe Deletion: Prevents deletion of books referenced in historical borrowing audits.
   - Live Search & Filtering by title, author, book ID, or category.
   - Multi-format import and export supporting **CSV**, **JSON**, and **XML**.

4. **Member & Borrower Registry**:
   - Register students and faculty with strict regex validation on emails and phone numbers.
   - Safe deletion protection ensuring historical loan references are never orphaned.

5. **Circulation Desk (Issue & Return Transactions)**:
   - Atomic transactions: Decrements available stock on issue; increments on return.
   - Enforces borrowing quotas (maximum 5 active loans per member).
   - Rejects issue attempts when physical stock is 0.
   - Rejects duplicate return attempts on closed loans.
   - Automated overdue loan detection with configurable fine assessment (₹2.00/day).

6. **External Book Discovery via Google Books REST API**:
   - Search external volumes by title, author, or keyword.
   - Non-blocking I/O via background multithreading (`BackgroundTaskWorker`) and asynchronous coroutines (`aiohttp`).
   - One-click "Import to Local Catalog" allowing independent local price and copy configuration.
   - Resilient error handling with rate-limit (HTTP 429) protection and offline fallback.

7. **Data Analytics & Statistical Engine**:
   - **Pandas**: Categorical grouping, aggregations, loan frequency rankings, and borrowing trends.
   - **NumPy**: Comprehensive descriptive statistics (Mean, Median, Standard Deviation, Min, Max, and Interquartile Percentiles) for book prices and borrowing durations.

8. **Module III Live Concurrency & Performance Benchmarks**:
   - Interactive GUI testbed comparing **Sequential Baseline**, **Multithreading (GIL contention)**, and **Multiprocessing (Multi-core ProcessPool)**.
   - High-resolution monotonic timing using `time.perf_counter()`.
   - Call stack profiling using standard library `cProfile`.

---

## 📂 Project Directory Structure

```
SMART LIBRARY MANAGEMENT AND BOOK ANALYTICS SYSTEM/
├── main.py                     # Primary Application Entry Point
├── config.py                   # Global System Configuration & Theme
├── requirements.txt            # Package Dependencies
├── README.md                   # Project Overview & Setup Instructions
├── .gitignore                  # Git Ignore Rules
│
├── database/                   # Data Access & Persistence Layer
│   ├── __init__.py
│   ├── connection.py           # SQLite Connection & Cursor Context Manager
│   ├── schema.py               # DDL Schema, Indexes & Sample Data Seeder
│   └── repositories.py         # Book, Member, Loan & Librarian Repositories
│
├── models/                     # Object-Oriented Domain Entities (Module I)
│   ├── __init__.py
│   ├── person.py               # Base Person Class (Encapsulation, Dunder methods)
│   ├── member.py               # Member Subclass (Inheritance & Polymorphism)
│   ├── librarian.py            # Librarian Subclass (PBKDF2 Password Hashing)
│   ├── book.py                 # Book Model (Operator Overloading `<` and `+`)
│   └── loan.py                 # Loan Model (Overdue & Fine Calculation)
│
├── services/                   # Business Logic & Functional Pipelines (Module II)
│   ├── __init__.py
│   ├── auth_service.py         # Authentication & `@require_librarian` Decorator
│   ├── book_service.py         # CRUD, lambda, map, filter, reduce & Iterator
│   ├── member_service.py       # Member Registration & Validation
│   ├── loan_service.py         # Circulation Rules & Atomic Transactions
│   └── report_service.py       # Operational Metrics & Multi-format Exporter
│
├── api/                        # REST API Integration Layer (Module V)
│   ├── __init__.py
│   └── google_books.py         # Sync (requests) & Async (aiohttp) API Client
│
├── analytics/                  # Data Intelligence & Visualization (Module IV)
│   ├── __init__.py
│   ├── data_processor.py       # Pandas Aggregations & NumPy Statistics
│   └── visualizations.py       # Matplotlib Embedded Tkinter Figure Generators
│
├── concurrency/                # Concurrency, Benchmarking & Profiling (Module III)
│   ├── __init__.py
│   ├── background_tasks.py     # Thread-safe GUI Queue & Thread Manager
│   ├── async_tasks.py          # AsyncIO Event Loop & Coroutine Workers
│   └── performance.py          # Multiprocessing Monte Carlo Benchmark & cProfile
│
├── gui/                        # Presentation Layer (Tkinter / TTK Desktop GUI)
│   ├── __init__.py
│   ├── styles.py               # Modern Indigo/Slate TTK Theme Styles
│   ├── login_view.py           # Role Selection & Authentication Screen
│   ├── main_window.py          # Main Window Frame & Sidebar Controller
│   ├── dashboard_view.py       # Live Metric Cards & Embedded Charts
│   ├── books_view.py           # Book Catalog Table & CRUD Dialogs
│   ├── members_view.py         # Member Directory Table & Registration Modals
│   ├── circulation_view.py     # Issue/Return Desk & Overdue Penalty Monitor
│   ├── analytics_view.py       # Multi-tab Deep Analytics & NumPy Tables
│   ├── api_search_view.py      # Google Books Online Discovery & Importer
│   └── concurrency_view.py     # Interactive CPU Benchmark & Profiling View
│
├── utils/                      # Utilities & Cross-Cutting Concerns
│   ├── __init__.py
│   ├── validators.py           # Regex Patterns & Functional Closures
│   ├── logging_config.py       # Rotating File Handler & Console Logging
│   └── file_handlers.py        # CSV, JSON & XML Importers and Exporters
│
├── tests/                      # Automated Test Suite (pytest)
│   ├── test_database.py        # DDL, Foreign Keys & Constraints
│   ├── test_validators.py      # Regular Expressions & Closures
│   ├── test_books.py           # Book Model, Operators & Functional Methods
│   ├── test_members.py         # Member Inheritance & Registration
│   ├── test_loans.py           # Transactions, Stock Guards & Overdues
│   ├── test_analytics.py       # Pandas, NumPy & Matplotlib Tests
│   ├── test_api.py             # Mocked Google Books REST API Calls
│   ├── test_gui.py             # Tkinter GUI View Instantiation Smoke Tests
│   └── test_e2e.py             # End-to-End Complete Circulation Lifecycle
│
├── data/                       # Local SQLite Database Storage
│   └── .gitkeep
├── logs/                       # Rotating Size-Managed Application Logs
│   └── .gitkeep
└── docs/                       # Project Documentation & Reports
    ├── advanced_concepts.md    # Syllabus Concept-to-Code Mapping
    ├── viva_questions.md       # 20 Comprehensive Viva Questions & Answers
    ├── test_plan.md            # QA Strategy & Verified Results
    ├── report.md               # Formal College Micro-Project Report
    └── screenshots/            # UI Captures
```

---

## 🚀 Quick Start Guide

You can run the system in two ways:
1. **Modern React Web Interface** (Primary, Interactive Web Application)
2. **Tkinter Desktop Interface** (Legacy / Desktop Demo)

---

### Option 1: Modern React + FastAPI Web Application (Recommended)

The modern stack runs a high-performance **FastAPI REST API** server on port 8000 and a **Vite + React + Tailwind CSS** frontend on port 5173.

#### 1. Start the FastAPI Backend Server
Open your terminal in the project root folder:
```bash
python api_server.py
```
> The REST API server will start at `http://127.0.0.1:8000`.  
> Interactive Swagger API Documentation is available at `http://127.0.0.1:8000/docs`.

#### 2. Start the React Frontend Development Server
Open a second terminal in the `frontend` directory:
```bash
cd frontend
npm run dev
```
> The React interface will be live at **`http://localhost:5173`**.

#### 3. Log In to the Web Portal
- **Username**: `admin`
- **Password**: `admin123`
- *(Or click the green **"1-Click Quick Demo Sign In"** button on the login screen for instant evaluation)*.

---

### Option 2: Tkinter Desktop GUI (Legacy Interface)

To launch the standalone Tkinter desktop interface:
```bash
python main.py
```
- **Login Credentials**: `admin` / `admin123`

---

## 🧪 Running Automated Tests

Run all 47 automated test cases (Backend Domain Models + Services + Analytics + Concurrency + REST API Endpoints) using `pytest`:
```bash
pytest -v
```
To run specific test modules:
```bash
pytest tests/test_api_server.py -v   # REST API endpoint tests
pytest tests/test_e2e.py -v          # End-to-end circulation lifecycle
pytest tests/test_analytics.py -v    # Pandas & NumPy analytics
pytest tests/test_books.py -v        # Book model & functional pipelines
```

---

## 🎓 Syllabus Concept Coverage (Modules I–V)

| Course Module | Key Topics Demonstrated | Exact File Implementation |
| :--- | :--- | :--- |
| **Module I: OOP** | Inheritance, Polymorphism, Encapsulation, `@property`, Dunder methods (`__str__`, `__len__`, `__bool__`), Operator Overloading (`<`, `+`), Class & Static methods. | `models/person.py`<br>`models/member.py`<br>`models/librarian.py`<br>`models/book.py` |
| **Module II: Functional** | `lambda`, `map()`, `filter()`, `functools.reduce()`, List/Set/Dict comprehensions, Generator function (`yield`), Custom Iterator, Decorator (`@require_librarian`), Closure. | `services/book_service.py`<br>`services/auth_service.py`<br>`utils/validators.py` |
| **Module III: Concurrency** | Multithreading (I/O & API calls), Multiprocessing (CPU-bound Monte Carlo simulation), AsyncIO (`aiohttp`), thread-safe `queue.Queue`, `time.perf_counter()`, `cProfile`. | `concurrency/background_tasks.py`<br>`concurrency/performance.py`<br>`concurrency/async_tasks.py` |
| **Module IV: Libraries** | Pandas DataFrame aggregations, NumPy statistical distributions, Matplotlib charts embedded in Tkinter, Regular expressions, CSV, JSON, and XML format handlers. | `analytics/data_processor.py`<br>`analytics/visualizations.py`<br>`utils/file_handlers.py` |
| **Module V: Application** | Tkinter & ttk desktop GUI, Google Books REST API consumption, SQLite relational database access with atomic transactions and rollback. | `main.py`<br>`gui/main_window.py`<br>`api/google_books.py`<br>`database/repositories.py` |

---

## 📄 Documentation & Viva Voce
- **Course Concept-to-Code Mapping**: [`docs/advanced_concepts.md`](docs/advanced_concepts.md)
- **20 Viva Questions & Comprehensive Answers**: [`docs/viva_questions.md`](docs/viva_questions.md)
- **Automated Test Plan & Verification Matrix**: [`docs/test_plan.md`](docs/test_plan.md)
- **College Micro-Project Report**: [`docs/report.md`](docs/report.md)
#   S M A R T - L I B R A R Y - M A N A G E M E N T - A N D - B O O K - A N A L Y T I C S - S Y S T E M  
 