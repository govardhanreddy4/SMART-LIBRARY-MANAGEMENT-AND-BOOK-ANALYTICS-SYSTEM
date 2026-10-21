# 📘 Smart Library Management and Book Analytics System
### Comprehensive Project & College Review Guide (Advanced Python Programming)

---

## 📑 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Complete System Architecture](#3-complete-system-architecture)
4. [Folder and File Structure](#4-folder-and-file-structure)
5. [End-to-End Data Flow](#5-end-to-end-data-flow)
6. [Database Design](#6-database-design)
7. [REST API Documentation](#7-rest-api-documentation)
8. [Python Concepts Used (Syllabus Modules I–V)](#8-python-concepts-used-syllabus-modules-iv)
9. [Analytics and Reports](#9-analytics-and-reports)
10. [Authentication and Security](#10-authentication-and-security)
11. [How to Run the Project on Windows](#11-how-to-run-the-project-on-windows)
12. [Testing & Verification](#12-testing--verification)
13. [Limitations and Future Improvements](#13-limitations-and-future-improvements)
14. [Review & Viva Voce Preparation](#14-review--viva-voce-preparation)
15. [Quick Revision & Demo Checklist](#15-quick-revision--demo-checklist)

---

## 1. Project Overview

### What the Project Does
The **Smart Library Management and Book Analytics System** is a modern, full-stack library automation and business intelligence software. It manages the complete lifecycle of books, students, and circulation (borrowing and returns), enforces institutional borrowing policies, automatically calculates overdue fines, integrates live with external book databases via the Google Books REST API, and performs statistical analysis on inventory valuation and reader borrowing behavior.

### The Problem It Solves
Traditional college libraries face several practical challenges:
1. **Manual Ledger Inefficiencies**: Manual paper logs or fragmented spreadsheets lead to stock count mismatches, unreturned books, and lost revenue.
2. **Delayed Overdue Tracking**: Lack of automated overdue calculation makes fine collection inconsistent.
3. **No Analytical Insights**: Librarians cannot easily see which subject categories are understocked, what the monetary valuation of their inventory is, or which books are most frequently read.
4. **Isolated Catalogs**: Librarians have to manually re-type book metadata (ISBN, publisher, title, author) rather than importing it directly from public online repositories.

### Main Objectives & Target Users
- **Librarians & Staff (Administrators)**: Manage book cataloging, member registration, checkouts, returns, inventory imports/exports, fine monitoring, and operational reporting.
- **Students & Faculty (Borrowers)**: Check book availability, discover new titles, and review borrowing rules.
- **Academic Goal**: Demonstrate end-to-end mastery of the **Advanced Python Programming** curriculum across Object-Oriented Design, Functional Programming, Concurrency & Performance, Data Handling (NumPy/Pandas), and Full-Stack Application Development.

### Key Implemented Features
- 🔐 **PBKDF2 Hashed Authentication**: Secure login supporting Administrator Librarians and Student Members with 100,000 salted iterations.
- 📊 **Real-Time Operational Dashboard**: 6 dynamic KPI cards, a Recharts category inventory bar chart, a circulation status donut chart, and recent activity logs.
- 📚 **Book Catalog Management**: Full CRUD (Create, Read, Update, Delete) with safe deletion guards, category filtering, live keyword search, and CSV/JSON/XML data import/export.
- 👥 **Member Management**: Registration with strict regular expression validation on email addresses and Indian/international phone numbers.
- 🔄 **Circulation Desk**: Atomic checkout and return transactions, strict 5-book quota limits per member, zero-stock checkout rejection, and automated ₹2.00/day overdue fine calculations.
- 🌐 **Google Books API Integration**: Live search across millions of global books with 1-click catalog import.
- 📈 **Pandas & NumPy Analytics**: Category inventory valuation aggregations, price distribution metrics (Mean, Median, Std Dev, 25th & 75th percentiles), and monthly circulation trendlines.
- ⚡ **Concurrency Lab**: In-browser parallel execution testbed comparing **Sequential Execution** vs. **ThreadPoolExecutor (GIL bound)** vs. **Multiprocessing Pool (Multi-core acceleration)**.
- 🖥️ **Dual Interface**: Primary modern **React SPA** web interface + Optional standalone **Tkinter desktop GUI**.

---

## 2. Technology Stack

### Backend Stack
- **Language**: Python 3.11
- **REST API Framework**: FastAPI 0.139.2 (asynchronous, high-performance web framework).
- **ASGI Server**: Uvicorn 0.51.0 (lightning-fast ASGI web server).
- **Data Validation**: Pydantic v2 (strict request and response schemas).
- **Database**: SQLite 3 (ACID-compliant relational database, serverless, zero-configuration).
- **Data Analysis**:
  - **Pandas 3.0.6**: DataFrame grouping, aggregations, time-series sorting, and multi-format conversion.
  - **NumPy 2.4.6**: Statistical array operations (mean, median, standard deviation, percentiles).
- **Visualizations**:
  - **Recharts 2.x**: Interactive client-side SVG charting in React.
  - **Matplotlib 3.11.2**: Embedded desktop canvas plotting for the Tkinter interface.
- **HTTP Clients**:
  - **requests 2.34.2**: Synchronous HTTP client for Google Books API.
  - **aiohttp 3.14.5**: Asynchronous coroutine-based HTTP client for non-blocking external requests.
- **Concurrency & Profiling**: `multiprocessing.Pool`, `concurrent.futures.ThreadPoolExecutor`, `asyncio`, `time.perf_counter`, and `cProfile`.
- **Testing**: `pytest 9.1.1` and `fastapi.testclient.TestClient`.

### Frontend Stack
- **Framework**: React 19.3.1 (Single Page Application architecture).
- **Build Tool**: Vite 8.3.4 (ultra-fast module bundler with Hot Module Replacement).
- **Styling**: Tailwind CSS 3.4.1 (utility-first modern CSS framework).
- **Icons**: Lucide React (modern feather-style UI iconography).
- **Routing**: React Router DOM v7 (client-side declarative routing and protected routes).
- **HTTP Client**: Axios (configured with interceptors, automatic JSON parsing, and proxy routing).

---

## 3. Complete System Architecture

The application is structured into **6 architectural tiers**:

```mermaid
flowchart TD
    subgraph Tier1["1. Client Presentation Tier"]
        ReactApp["React 19 Single Page App<br/>(Vite + Tailwind + Recharts)"]
        TkinterApp["Legacy Tkinter Desktop GUI<br/>(Tkinter/ttk + Matplotlib)"]
    end

    subgraph Tier2["2. API & Routing Tier (FastAPI)"]
        Server["api_server.py (Uvicorn ASGI :8000)"]
        FastAPIApp["server/app.py (CORS + Middleware)"]
        Routers["server/routers/<br/>(auth, books, members, loans, analytics, concurrency)"]
        Schemas["server/schemas.py (Pydantic v2 Models)"]
    end

    subgraph Tier3["3. Application & Business Logic Tier"]
        AuthSvc["AuthService (services/auth_service.py)"]
        BookSvc["BookService (services/book_service.py)"]
        MemberSvc["MemberService (services/member_service.py)"]
        LoanSvc["LoanService (services/loan_service.py)"]
        ReportSvc["ReportService (services/report_service.py)"]
    end

    subgraph Tier4["4. Analytics & Concurrency Tier"]
        DataProc["DataProcessor (analytics/data_processor.py - Pandas/NumPy)"]
        PerfBench["PerformanceBenchmarker (concurrency/performance.py)"]
        GBooksAPI["GoogleBooksAPI (api/google_books.py)"]
    end

    subgraph Tier5["5. Data Access Tier (Repositories)"]
        BookRepo["BookRepository (database/repositories.py)"]
        MemberRepo["MemberRepository (database/repositories.py)"]
        LoanRepo["LoanRepository (database/repositories.py)"]
        LibrarianRepo["LibrarianRepository (database/repositories.py)"]
    end

    subgraph Tier6["6. Storage & Database Tier"]
        ConnContext["Connection Context Manager (database/connection.py)"]
        SQLiteDB[("SQLite 3 Database<br/>data/library.db")]
    end

    ReactApp -->|HTTP JSON /api| Server
    Server --> FastAPIApp
    FastAPIApp --> Routers
    Routers --> Schemas
    Routers --> Tier3
    Routers --> Tier4
    TkinterApp -.->|Direct Python Calls| Tier3
    TkinterApp -.->|Direct Python Calls| Tier4
    Tier3 --> Tier5
    Tier4 --> ConnContext
    Tier5 --> ConnContext
    ConnContext --> SQLiteDB
```

### Communication Flow:
1. **Frontend to API**: The React frontend sends HTTP requests (`GET`, `POST`, `PUT`, `DELETE`) to the `/api` prefix. The Vite development server automatically proxies these requests to `http://127.0.0.1:8000`.
2. **API to Services**: FastAPI routers validate request JSON using Pydantic schemas, unpack the parameters, and invoke business service methods.
3. **Services to Repositories**: Services enforce domain logic (quotas, stock availability, business calculations, regex verification) and delegate database commands to Repositories.
4. **Repositories to SQLite**: Repositories use parameterized SQL queries (`?`) executed inside transactional context managers, preventing SQL injection and guaranteeing database consistency.

---

## 4. Folder and File Structure

```
SMART LIBRARY MANAGEMENT AND BOOK ANALYTICS SYSTEM/
├── api_server.py                      # ASGI Server Launcher (runs Uvicorn on 127.0.0.1:8000)
├── main.py                            # Standalone Desktop Tkinter GUI Launcher (legacy)
├── config.py                          # Global configuration (paths, DB settings, rules, fines)
├── requirements.txt                   # Complete Python dependencies specification
├── run_backend.bat                    # 1-Click Windows batch script to start FastAPI backend
├── run_frontend.bat                   # 1-Click Windows batch script to start React frontend
├── run_desktop.bat                    # 1-Click Windows batch script to launch Tkinter desktop app
│
├── frontend/                          # Modern React Web Application (Vite SPA)
│   ├── vite.config.js                 # Dev server setup + reverse proxy (/api -> :8000)
│   ├── tailwind.config.js             # Styling configuration & custom color palette
│   ├── package.json                   # NPM dependencies manifest (React, Recharts, Lucide, Axios)
│   ├── index.html                     # HTML5 single page entry point
│   └── src/
│       ├── main.jsx                   # React root rendering and DOM attachment
│       ├── App.jsx                    # Route hierarchy & ProtectedRoute wrapper
│       ├── index.css                  # Tailwind CSS base directives & custom scrollbars
│       ├── api/
│       │   └── client.js              # Axios instance, response interceptors & typed API calls
│       ├── context/
│       │   └── AuthContext.jsx        # User authentication state & localStorage persistence
│       ├── components/layout/
│       │   ├── AppLayout.jsx          # Shell with Sidebar, Topbar, and dynamic page metadata
│       │   ├── Sidebar.jsx            # Dark navigation sidebar with active link indicators
│       │   └── Topbar.jsx             # Live server status badge & ACID database indicator
│       └── pages/
│           ├── LoginPage.jsx          # Authentication portal & 1-click quick demo login
│           ├── DashboardPage.jsx      # 6 KPI cards, Recharts category bar & circulation donut
│           ├── BooksPage.jsx          # Catalog table, live search/filter, CRUD modals, export
│           ├── MembersPage.jsx        # Member directory, registration modal with regex check
│           ├── CirculationPage.jsx    # Issue/checkout modal, 1-click return, overdue fines
│           ├── AnalyticsPage.jsx      # Pandas aggregation table, NumPy statistical metrics
│           ├── BookDiscoveryPage.jsx  # Google Books REST API search & catalog import
│           └── ConcurrencyPage.jsx    # Parallel benchmark runner (Sequential vs Threads vs MP)
│
├── server/                            # FastAPI REST API Backend
│   ├── app.py                         # FastAPI instance, CORS middleware, router aggregation
│   ├── schemas.py                     # Pydantic v2 validation models for all request bodies
│   ├── dependencies.py                # Dependency injection providers for services & DB
│   └── routers/
│       ├── auth.py                    # /api/auth (login, logout, me, register-librarian)
│       ├── dashboard.py               # /api/dashboard (summary, charts, recent-loans)
│       ├── books.py                   # /api/books (CRUD, categories, functional-demo, import/export)
│       ├── members.py                 # /api/members (CRUD, export)
│       ├── loans.py                   # /api/loans (all, active, overdue, issue, return, export)
│       ├── analytics.py               # /api/analytics (category-breakdown, price-stats, trends)
│       ├── google_books.py            # /api/google-books (search, import-catalog)
│       ├── concurrency.py             # /api/concurrency (live parallel benchmark executor)
│       └── reports.py                 # /api/reports (summary report, multi-format download)
│
├── models/                            # Object-Oriented Domain Entities (Module I)
│   ├── person.py                      # Abstract Base Class Person (encapsulation, dunder methods)
│   ├── member.py                      # Member subclass (inheritance, quota, polymorphism)
│   ├── librarian.py                   # Librarian subclass (PBKDF2-HMAC-SHA256 password hashing)
│   ├── book.py                        # Book class (operator overloading <, +, __len__, __bool__)
│   └── loan.py                        # Loan circulation model with overdue & fine computation
│
├── services/                          # Business Logic & Functional Pipelines (Module II)
│   ├── auth_service.py                # AuthService with @require_librarian decorator
│   ├── book_service.py                # BookService (map, filter, reduce, comprehensions, iterators)
│   ├── member_service.py              # Member registration & contact lifecycle management
│   ├── loan_service.py                # Circulation rules, quota checks & atomic transactions
│   └── report_service.py              # KPI calculation & multi-format report generator
│
├── database/                          # Persistence & Data Access Layer
│   ├── connection.py                  # Thread-safe SQLite connection factory & cursor context manager
│   ├── schema.py                      # SQL DDL schemas, indexes, and initial starter data seeder
│   └── repositories.py                # BookRepository, MemberRepository, LoanRepository, LibrarianRepository
│
├── analytics/                         # Data Science & Statistical Engines (Module IV)
│   ├── data_processor.py              # DataProcessor (Pandas DataFrame aggregations, NumPy statistics)
│   └── visualizations.py              # Matplotlib figure generators (for Tkinter desktop interface)
│
├── concurrency/                       # Performance & Parallel Computing (Module III)
│   ├── performance.py                 # PerformanceBenchmarker (Sequential vs ThreadPool vs ProcessPool)
│   ├── background_tasks.py            # Thread-safe TaskWorker with queue.Queue for Tkinter UI
│   └── async_tasks.py                 # AsyncBookSearcher using asyncio and aiohttp
│
├── api/                               # External Web Services Integration (Module V)
│   └── google_books.py                # GoogleBooksAPI client (requests sync + aiohttp async)
│
├── utils/                             # Cross-Cutting Infrastructure
│   ├── validators.py                  # Regex patterns for IDs, emails, phones + range closures
│   ├── file_handlers.py               # DataExporter and DataImporter for CSV, JSON, and XML
│   └── logging_config.py              # Size-rotating file logger (library_system.log)
│
├── tests/                             # Automated Test Suite (47/47 passing tests)
│   ├── test_api_server.py             # FastAPI TestClient endpoint integration tests (9 tests)
│   ├── test_database.py               # DDL, indexes, and foreign key integrity tests
│   ├── test_validators.py             # Regex and closure validation tests
│   ├── test_books.py                  # Book domain model, operator overloading, and functional methods
│   ├── test_members.py                # Member inheritance and polymorphism tests
│   ├── test_loans.py                  # Circulation atomic transactions and quota tests
│   ├── test_analytics.py              # Pandas DataFrame and NumPy statistical tests
│   ├── test_api.py                    # Mocked Google Books REST API tests
│   ├── test_gui.py                    # Desktop GUI instantiation smoke tests
│   └── test_e2e.py                    # End-to-end full circulation lifecycle test
│
├── data/                              # SQLite database storage (library.db)
├── logs/                              # Size-managed rotating logs (library_system.log)
└── docs/                              # Project documentation, viva guide, and evaluation reports
```

---

## 5. End-to-End Data Flow

### 1. User Login
1. **React UI**: User submits credentials on `LoginPage.jsx` (e.g., `admin` / `admin123`).
2. **API Client**: `authApi.login(username, password)` in `client.js` sends `POST /api/auth/login`.
3. **Router**: `server/routers/auth.py` receives request parsed by `LoginRequest` schema.
4. **Service**: `AuthService.login(username, password)` calls `LibrarianRepository.get_by_username()`.
5. **Database**: Fetches stored `password_hash` and `salt`.
6. **Domain Logic**: `Librarian.verify_password()` recomputes `hashlib.pbkdf2_hmac` using the retrieved salt.
7. **Response**: If valid, returns HTTP 200 with user profile; React `AuthContext` stores user in state and `localStorage` and navigates to Dashboard (`/`).

### 2. Adding a Book
1. **React UI**: Librarian fills the "Add Book" modal on `BooksPage.jsx` and clicks submit.
2. **API Client**: `booksApi.create(payload)` sends `POST /api/books`.
3. **Router**: `server/routers/books.py` validates fields with `BookCreate` schema (`price >= 0`, `total_copies >= 1`).
4. **Service**: `BookService.add_book()` executes `Validators.validate_book_inputs()` (regex checks on `book_id`, non-empty strings, positive numeric stock).
5. **Model**: Creates domain instance `Book(...)`.
6. **Repository**: `BookRepository.add_book()` runs parameterized `INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?)`.
7. **Database**: SQLite executes query, commits transaction, and writes to disk.
8. **UI Update**: Router returns HTTP 201; React closes modal, shows green success banner, and re-fetches updated book catalog.

### 3. Registering a Member
1. **React UI**: Librarian submits member details on `MembersPage.jsx`.
2. **API Client**: `membersApi.create(payload)` sends `POST /api/members`.
3. **Router**: `server/routers/members.py` validates with `MemberCreate`.
4. **Service**: `MemberService.register_member()` runs regex checks via `Validators.validate_member_inputs()`:
   - Email format: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
   - Phone format: `^(\+91[\-\s]?)?[0]?[6789]\d{9}$`
5. **Repository**: `MemberRepository.add_member()` inserts record into `members` table.
6. **UI Update**: HTTP 201 response returned; member table immediately reflects new registration.

### 4. Issuing a Book
1. **React UI**: Librarian selects book and member on `CirculationPage.jsx` and sets loan duration (default 14 days).
2. **API Client**: `loansApi.issue(payload)` sends `POST /api/loans/issue`.
3. **Service Logic**: `LoanService.issue_book()` executes 4 critical validation checks:
   - *Check 1*: Verifies member exists in database.
   - *Check 2*: Verifies member has not exceeded maximum borrowing quota (`active_loans < 5`).
   - *Check 3*: Verifies book exists and physical stock is available (`available_copies > 0`).
   - *Check 4*: Computes `issue_date` (today) and `due_date` (today + 14 days).
4. **Atomic Transaction**: `LoanRepository.issue_book_transaction()` executes inside a single database transaction:
   ```sql
   INSERT INTO loans (book_id, member_id, issue_date, due_date, status) VALUES (?, ?, ?, ?, 'ACTIVE');
   UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?;
   ```
5. **UI Update**: Loan ID returned with HTTP 201; loans table and dashboard cards auto-refresh.

### 5. Returning a Book
1. **React UI**: Librarian clicks "Return" button on an active loan row in `CirculationPage.jsx`.
2. **API Client**: `loansApi.returnBook(loanId)` sends `POST /api/loans/{loanId}/return`.
3. **Atomic Transaction**: `LoanRepository.return_book_transaction()` verifies loan is active, sets `return_date = date.today()` and `status = 'RETURNED'`, and increments book stock:
   ```sql
   UPDATE loans SET return_date = ?, status = 'RETURNED' WHERE loan_id = ?;
   UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?;
   ```
4. **UI Update**: Stock is replenished on shelves; loan badge updates to `RETURNED`.

### 6. Viewing Analytics and Reports
1. **React UI**: User navigates to `AnalyticsPage.jsx`.
2. **API Client**: Makes parallel calls to `/api/analytics/category-breakdown`, `/api/analytics/price-stats`, `/api/analytics/loan-duration-stats`, and `/api/analytics/monthly-trends`.
3. **Analytics Engine**: `DataProcessor` in `analytics/data_processor.py` queries SQLite into Pandas DataFrames:
   - Computes `valuation = price * total_copies`.
   - Groups by `category` with aggregations (`title_count`, `total_copies`, `available_copies`, `issued_copies`, `valuation`).
   - Extracts NumPy array of prices: calculates `np.mean()`, `np.median()`, `np.std()`, `np.min()`, `np.max()`, `np.percentile(prices, 25)`, and `np.percentile(prices, 75)`.
4. **UI Update**: Recharts renders valuation bar chart and monthly trendline; NumPy metrics are displayed in statistical summary cards.

---

## 6. Database Design

The system uses **SQLite 3** (`data/library.db`) configured with foreign key enforcement and transactional write safety.

```mermaid
erDiagram
    BOOKS ||--o{ LOANS : "borrowed in"
    MEMBERS ||--o{ LOANS : "checks out"
    LIBRARIANS ||--o{ BOOKS : "manages"

    BOOKS {
        TEXT book_id PK "Unique identifier (e.g. BK-1001)"
        TEXT title "Title of publication"
        TEXT author "Author names"
        TEXT category "Subject genre"
        REAL price "Unit price >= 0"
        INTEGER total_copies "Total inventory >= 1"
        INTEGER available_copies "On shelf (0 to total_copies)"
    }

    MEMBERS {
        TEXT member_id PK "Unique ID (e.g. MEM-001)"
        TEXT name "Full member name"
        TEXT email "Unique regex validated email"
        TEXT phone "Contact phone number"
        TEXT created_at "ISO-8601 registration timestamp"
    }

    LOANS {
        INTEGER loan_id PK "Autoincrement loan ID"
        TEXT book_id FK "References books(book_id)"
        TEXT member_id FK "References members(member_id)"
        TEXT issue_date "Date checked out (YYYY-MM-DD)"
        TEXT due_date "Expected return date"
        TEXT return_date "Actual date returned (NULL if open)"
        TEXT status "CHECK ('ACTIVE', 'RETURNED', 'OVERDUE')"
    }

    LIBRARIANS {
        TEXT librarian_id PK "Unique staff ID (e.g. LIB-001)"
        TEXT username "Unique login username"
        TEXT password_hash "PBKDF2-HMAC-SHA256 hex string"
        TEXT salt "Cryptographic random salt"
        TEXT name "Staff member name"
        TEXT email "Contact email"
        TEXT phone "Contact phone"
        INTEGER is_admin "1 for Admin, 0 for Staff"
    }
```

### Table Integrity & Constraints:
- **Foreign Key Restraints**: `FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE RESTRICT` and `FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE RESTRICT`. Books or members referenced in borrowing histories cannot be accidentally deleted.
- **Check Constraints**:
  - `CHECK(price >= 0)`
  - `CHECK(total_copies >= 1)`
  - `CHECK(available_copies >= 0 AND available_copies <= total_copies)`
  - `CHECK(status IN ('ACTIVE', 'RETURNED', 'OVERDUE'))`
- **Performance Indexes**:
  - `idx_books_category ON books(category)`
  - `idx_books_title ON books(title)`
  - `idx_loans_status ON loans(status)`
  - `idx_loans_book_id ON loans(book_id)`
  - `idx_loans_member_id ON loans(member_id)`
  - `idx_loans_dates ON loans(issue_date, due_date)`

---

## 7. REST API Documentation

Base URL: `http://127.0.0.1:8000` | Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

| HTTP Method | Endpoint | Purpose | Request Body / Query | Success Response | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `GET` | `/api/health` | Operational health check | None | `{"status": "healthy", ...}` | 200 |
| `POST` | `/api/auth/login` | User authentication | `{"username": "...", "password": "..."}` | `{"success": true, "user": {...}}` | 200 / 401 |
| `POST` | `/api/auth/logout` | Clear user session | None | `{"success": true, "message": "..."}` | 200 |
| `GET` | `/api/auth/me` | Fetch current session user | None | `{"authenticated": true, "user": {...}}` | 200 |
| `GET` | `/api/dashboard/summary`| Live KPI summary figures | None | `{"total_titles": 10, "total_copies": 40, ...}` | 200 |
| `GET` | `/api/dashboard/charts` | Chart datasets & recent loans | None | `{"category_data": [...], "circulation_status": [...]}` | 200 |
| `GET` | `/api/books` | List books with search/filter| Query: `?query=...&category=...` | `[{"book_id": "BK-1001", ...}]` | 200 |
| `GET` | `/api/books/{id}` | Fetch book by ID | Path: `id` | `{"book_id": "BK-1001", ...}` | 200 / 404 |
| `POST` | `/api/books` | Add new catalog book | `BookCreate` JSON | `{"success": true, "book": {...}}` | 201 / 400 |
| `PUT` | `/api/books/{id}` | Update book details | `BookUpdate` JSON | `{"success": true, "book": {...}}` | 200 / 400 |
| `DELETE` | `/api/books/{id}` | Safe delete book record | Path: `id` | `{"success": true, "message": "..."}` | 200 / 400 |
| `GET` | `/api/books/categories` | Unique category list | None | `["Computer Science", "Databases", ...]` | 200 |
| `GET` | `/api/books/functional-demo`| Python Module II demo stats | None | `{"total_valuation_reduce": ..., "categories_set_comp": [...]}` | 200 |
| `POST` | `/api/books/import` | Upload CSV/JSON catalog file | `multipart/form-data` | `{"success": true, "details": {...}}` | 200 / 400 |
| `GET` | `/api/books/export/{fmt}` | Download CSV/JSON/XML | Path: `csv`, `json`, `xml` | Streamed File Attachment | 200 |
| `GET` | `/api/members` | List members with search | Query: `?query=...` | `[{"member_id": "MEM-001", ...}]` | 200 |
| `POST` | `/api/members` | Register new member | `MemberCreate` JSON | `{"success": true, "member": {...}}` | 201 / 400 |
| `PUT` | `/api/members/{id}` | Update member contact | `MemberUpdate` JSON | `{"success": true, "member": {...}}` | 200 / 400 |
| `DELETE` | `/api/members/{id}` | Safe delete member | Path: `id` | `{"success": true, "message": "..."}` | 200 / 400 |
| `GET` | `/api/loans` | Complete circulation history | None | `[{"loan_id": 1, ...}]` | 200 |
| `GET` | `/api/loans/active` | Current active loans | None | `[{"loan_id": 1, "status": "ACTIVE", ...}]` | 200 |
| `GET` | `/api/loans/overdue` | Overdue loans + fine amounts | None | `[{"loan_id": 2, "fine_amount": 34.0, ...}]` | 200 |
| `POST` | `/api/loans/issue` | Checkout / Issue book | `{"book_id": "...", "member_id": "...", "loan_days": 14}` | `{"success": true, "loan_id": 6}` | 201 / 400 |
| `POST` | `/api/loans/{id}/return` | Process book return | Path: `id` | `{"success": true, "message": "..."}` | 200 / 400 |
| `GET` | `/api/analytics/category-breakdown` | Pandas category valuation | None | `[{"category": "...", "valuation": ...}]` | 200 |
| `GET` | `/api/analytics/price-stats` | NumPy price statistics | None | `{"mean": 820.5, "median": 750.0, "std": ...}` | 200 |
| `GET` | `/api/analytics/loan-duration-stats`| NumPy duration stats | None | `{"mean_days": 13.5, "median_days": 14.0}` | 200 |
| `GET` | `/api/analytics/monthly-trends` | Time-series loan counts | None | `[{"period": "2026-09", "loan_count": 5}]` | 200 |
| `GET` | `/api/google-books/search` | Live Google Books search | Query: `?q=...` | `[{"title": "...", "thumbnail": "...", ...}]` | 200 |
| `POST` | `/api/google-books/import-catalog`| Import Google Book to DB | `GoogleBookImportRequest` JSON | `{"success": true, "book": {...}}` | 201 / 400 |
| `POST` | `/api/concurrency/benchmark` | Run parallel benchmark | `{"total_simulations": 100000, "num_chunks": 8}` | `{"data": {"sequential_time_sec": ..., "threading_time_sec": ..., "multiprocessing_time_sec": ..., "multiprocessing_speedup": ...}}` | 200 |

---

## 8. Python Concepts Used (Syllabus Modules I–V)

### Module I: Object-Oriented Programming (OOP)
1. **Classes and Encapsulation**:
   - *File*: `models/person.py`
   - *Implementation*: Abstract class `Person` using private attributes `_name`, `_email`, `_phone` with `@property` getters and setters.
   ```python
   @property
   def email(self) -> str:
       return self._email
   ```
2. **Inheritance & Method Overriding (Polymorphism)**:
   - *File*: `models/member.py` and `models/librarian.py`
   - *Implementation*: Both classes inherit from `Person` and override the abstract method `get_role_display()`:
   ```python
   class Member(Person):
       def get_role_display(self) -> str:
           return "Student Member"
   ```
3. **Special (Dunder) Methods**:
   - *File*: `models/book.py`
   - *Implementation*: Implements `__str__`, `__repr__`, `__len__` (returns available copies), and `__bool__` (ensures books with 0 available stock still evaluate truthy in condition checks).
4. **Operator Overloading**:
   - *File*: `models/book.py`
   - *Implementation*: Overloads `<` (`__lt__`) to enable natural sorting of book objects by price, and `+` (`__add__`) to combine inventory stock counts of identical books:
   ```python
   def __lt__(self, other: "Book") -> bool:
       return self.price < other.price
   ```
5. **Class Methods & Static Methods**:
   - *File*: `models/librarian.py`
   - *Implementation*: Static method `Librarian.hash_password(password)` and class method `Book.from_row(row)` in `models/book.py`.

---

### Module II: Functional Programming & Iterators
1. **Lambda Expressions**:
   - *File*: `services/book_service.py`
   - *Implementation*: Used inside higher-order pipelines: `lambda b: b.is_available`.
2. **`filter()` and `map()`**:
   - *File*: `services/book_service.py` (lines 144–155)
   - *Implementation*:
   ```python
   # filter() with lambda
   available_books = list(filter(lambda b: b.is_available, catalog))
   # map() with lambda
   summaries = list(map(lambda b: f"[{b.book_id}] {b.title} - ₹{b.price:.2f}", catalog))
   ```
3. **`functools.reduce()`**:
   - *File*: `services/book_service.py` (lines 156–164)
   - *Implementation*: Computes total inventory monetary valuation:
   ```python
   total_val = reduce(lambda acc, b: acc + (b.price * b.total_copies), catalog, 0.0)
   ```
4. **Comprehensions**:
   - *File*: `services/book_service.py` (lines 165–182)
   - *Set Comprehension*: `{b.category for b in catalog}` (extracts unique categories).
   - *Dictionary Comprehension*: `{b.book_id: b.available_copies for b in catalog}` (quick stock lookup table).
   - *List Comprehension with Condition*: `[b.title for b in catalog if b.available_copies <= threshold]` (filters low-stock titles).
5. **Generators & Iterators**:
   - *File*: `services/book_service.py`
   - *Custom Iterator*: `CatalogIterator` implements `__iter__` and `__next__`.
   - *Generator Function*: `stream_books_generator(batch_size)` uses `yield` to stream book batches.
6. **Decorators**:
   - *File*: `services/auth_service.py` (lines 18–35)
   - *Implementation*: Custom decorator `@require_librarian` using `functools.wraps` to restrict administrative actions to verified staff accounts.
7. **Closures**:
   - *File*: `utils/validators.py` (lines 62–74)
   - *Implementation*: `create_range_validator(min_val, max_val)` returns an inner validation function capturing the numerical boundary variables.

---

### Module III: Concurrency and Performance
1. **Multithreading**:
   - *File*: `concurrency/background_tasks.py` and `concurrency/performance.py`
   - *Implementation*: `ThreadPoolExecutor(max_workers=4)` executes concurrent I/O-bound tasks and reveals GIL lock contention on CPU-bound benchmarks.
2. **Multiprocessing**:
   - *File*: `concurrency/performance.py` (lines 93–109)
   - *Implementation*: `multiprocessing.Pool(processes=cpu_count())` distributes stochastic Monte Carlo calculations across all CPU cores, bypassing the Python GIL.
3. **AsyncIO**:
   - *File*: `concurrency/async_tasks.py` and `api/google_books.py`
   - *Implementation*: `asyncio` event loop and `aiohttp.ClientSession` execute asynchronous, non-blocking HTTP requests to the Google Books API.
4. **Execution-Time Measurement**:
   - *File*: `concurrency/performance.py`
   - *Implementation*: Sub-microsecond timing using `time.perf_counter()`.
5. **Call-Stack Profiling**:
   - *File*: `concurrency/performance.py` (lines 133–145)
   - *Implementation*: `cProfile.Profile()` profiles execution time and prints top cumulative function calls via `pstats.Stats`.

---

### Module IV: Data Handling & Visualization
1. **Pandas DataFrames**:
   - *File*: `analytics/data_processor.py`
   - *Implementation*: Reads SQL tables via `pd.read_sql_query`, cleans types, calculates `valuation = price * total_copies`, groups by category, and sorts trends.
2. **NumPy Arrays & Statistics**:
   - *File*: `analytics/data_processor.py` (lines 85–133)
   - *Implementation*: Converts Pandas series to `prices = df['price'].to_numpy()` and calculates `np.mean()`, `np.median()`, `np.std()`, `np.min()`, `np.max()`, and `np.percentile()`.
3. **Matplotlib Visualizations**:
   - *File*: `analytics/visualizations.py`
   - *Implementation*: Generates bar charts, donut charts, and line plots with custom color schemes, embedded directly into Tkinter `FigureCanvasTkAgg`.
4. **Regular Expressions (`re`)**:
   - *File*: `utils/validators.py`
   - *Implementation*: Compiles regex patterns to validate Book IDs (`^BK-\d{3,6}$`), Member IDs (`^MEM-\d{3,6}$`), email addresses, and phone numbers.
5. **Structured Formats (CSV, JSON, XML)**:
   - *File*: `utils/file_handlers.py`
   - *Implementation*: Implements `DataExporter` and `DataImporter` supporting CSV (`csv.DictReader`/`DictWriter`), JSON (`json.dump`/`load`), and XML (`xml.etree.ElementTree`).

---

### Module V: Application Development
1. **FastAPI REST API**: Layer exposing 20+ REST endpoints with Pydantic request models and CORS middleware.
2. **React SPA**: Interactive web user interface with client-side routing, Recharts, and Axios integration.
3. **Tkinter GUI**: Legacy desktop interface built with `tkinter` and `ttk`.
4. **SQLite Database**: Relational storage with foreign key constraints, indexes, and atomic ACID transactions.
5. **Google Books REST API**: External web service consumption via HTTP GET.

---

## 9. Analytics and Reports

The system calculates metrics from actual database records:

### 1. Key Metrics (Dashboard Summary)
- `total_titles`: `SELECT COUNT(*) FROM books`
- `total_copies`: `SELECT SUM(total_copies) FROM books`
- `available_copies`: `SELECT SUM(available_copies) FROM books`
- `issued_copies`: Calculated as `total_copies - available_copies` (represents books currently in the possession of members).
- `active_members`: `SELECT COUNT(*) FROM members`
- `overdue_loans`: `SELECT COUNT(*) FROM loans WHERE return_date IS NULL AND due_date < date('now')`

### 2. Category Analytics (Pandas Engine)
`analytics/data_processor.py::get_category_analytics()` groups the catalog by category and computes:
- Total titles count per category
- Total copies and available copies
- Issued copies in circulation
- Average book price per category
- Total inventory valuation: $\sum (\text{price} \times \text{total\_copies})$

### 3. Price Statistics (NumPy Engine)
`analytics/data_processor.py::calculate_price_statistics_numpy()` calculates:
- Mean Price: Average acquisition cost across all catalogued titles.
- Median Price: The central price point, unaffected by expensive reference book outliers.
- Standard Deviation: Price dispersion indicator.
- Minimum & Maximum: The lowest and highest priced books.
- 25th (Q1) & 75th (Q3) Percentiles: Demonstrates interquartile distribution analysis.

---

## 10. Authentication and Security

### Authentication Architecture
1. **No Plaintext Passwords**: Passwords are never stored in the database.
2. **PBKDF2-HMAC-SHA256**: Passwords are hashed using Python's standard library `hashlib.pbkdf2_hmac` with a unique 16-byte cryptographic salt generated via `os.urandom(16)` and 100,000 hashing iterations.
3. **Constant-Time Verification**: Uses `hmac.compare_digest` to prevent timing attack vulnerabilities.
4. **Default Administrator Credentials**:
   - **Username**: `admin`
   - **Password**: `admin123`
   *(Auto-seeded into `librarians` table during first database initialization).*

### Security Best Practices Implemented:
- **Parameterized SQL**: All database operations use parameter substitution `?`, neutralizing SQL injection attempts.
- **Foreign Key Cascade Protection**: SQLite foreign key constraints use `ON DELETE RESTRICT` to prevent orphan loan records.

### Limitations & Production Recommendations:
- *Current Project Scope*: Auth session is maintained client-side in React `localStorage`.
- *Production Recommendations*:
  1. Add JWT (JSON Web Tokens) with cryptographic signatures and expiration times.
  2. Implement HTTPS/TLS encryption.
  3. Change the default `admin` password upon first login.
  4. Store the salt length and iteration count in environment variables (`.env`).

---

## 11. How to Run the Project on Windows

### Prerequisites
1. **Python 3.11** installed and added to your Windows PATH.
2. **Node.js (v18+) and npm** installed.

---

### Method A: One-Click Windows Batch Scripts (Quickest)
1. Double-click `run_backend.bat` in the project root folder.
   > Starts the FastAPI backend at `http://127.0.0.1:8000`.
2. Double-click `run_frontend.bat` in the project root folder.
   > Starts the React Vite frontend at `http://localhost:5173`.
3. Open your browser and go to **`http://localhost:5173`**.

---

### Method B: Manual Command-Line Startup

#### Step 1: Install Python Dependencies
Open PowerShell or Command Prompt in the project root:
```powershell
pip install -r requirements.txt
```

#### Step 2: Start the FastAPI Backend Server
In the root directory, run:
```powershell
python api_server.py
```
- Server URL: `http://127.0.0.1:8000`
- Interactive Swagger API Docs: `http://127.0.0.1:8000/docs`

#### Step 3: Install and Start the React Frontend
Open a **second terminal**, change into the `frontend` folder, and run:
```powershell
cd frontend
npm install
npm run dev
```
- Frontend Web App: **`http://localhost:5173`**

#### Step 4: Login to the Portal
- Enter username `admin` and password `admin123`, or click the green **"1-Click Quick Demo Sign In"** button on the login screen.

---

### Method C: Launching the Desktop Tkinter GUI (Legacy Demo)
In the project root directory, run:
```powershell
python main.py
```
*(Or double-click `run_desktop.bat`).*

---

### Common Troubleshooting Tips
| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `Port 8000 already in use` | Another process is using port 8000 | Close the existing terminal, or change the port in `api_server.py` to 8001. |
| `npm : File ... cannot be loaded because running scripts is disabled` | Windows PowerShell ExecutionPolicy restriction | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in PowerShell, or use standard Command Prompt (`cmd.exe`). |
| `Vite proxy error: ECONNREFUSED` | React is trying to call the API, but the backend is not running | Start `python api_server.py` before interacting with the React app. |

---

## 12. Testing & Verification

The project includes an automated test suite executed with `pytest`:

### Run Command:
```powershell
pytest -v
```

### Verified Test Results: **47 Passed in ~30 seconds (100% Passing)**
```
tests/test_api_server.py::test_health_check PASSED                       [  2%]
tests/test_api_server.py::test_auth_login_success_and_failure PASSED     [  4%]
tests/test_api_server.py::test_dashboard_summary PASSED                  [  6%]
tests/test_api_server.py::test_dashboard_charts PASSED                   [  8%]
tests/test_api_server.py::test_books_crud PASSED                         [ 10%]
tests/test_api_server.py::test_members_crud PASSED                       [ 12%]
tests/test_api_server.py::test_loans_endpoints PASSED                    [ 14%]
tests/test_api_server.py::test_analytics_endpoints PASSED                [ 17%]
tests/test_api_server.py::test_concurrency_benchmark_endpoint PASSED     [ 19%]
tests/test_database.py::test_database_initialization PASSED              [ 21%]
tests/test_database.py::test_foreign_key_enforcement PASSED             [ 23%]
tests/test_validators.py::test_email_validation PASSED                   [ 25%]
tests/test_validators.py::test_phone_validation PASSED                   [ 27%]
tests/test_validators.py::test_range_validator_closure PASSED            [ 29%]
tests/test_books.py::test_book_model_methods PASSED                      [ 31%]
tests/test_books.py::test_operator_overloading PASSED                    [ 34%]
tests/test_books.py::test_functional_filter_and_map PASSED               [ 36%]
tests/test_books.py::test_reduce_valuation PASSED                        [ 38%]
tests/test_books.py::test_custom_iterator PASSED                         [ 40%]
tests/test_members.py::test_member_inheritance PASSED                    [ 42%]
tests/test_members.py::test_member_validation PASSED                     [ 44%]
tests/test_loans.py::test_issue_and_return_transaction PASSED            [ 46%]
tests/test_loans.py::test_quota_enforcement PASSED                       [ 48%]
tests/test_loans.py::test_zero_stock_rejection PASSED                    [ 51%]
tests/test_loans.py::test_overdue_and_fine_calculation PASSED           [ 53%]
tests/test_analytics.py::test_pandas_category_aggregation PASSED         [ 55%]
tests/test_analytics.py::test_numpy_price_statistics PASSED              [ 57%]
tests/test_analytics.py::test_numpy_loan_duration_statistics PASSED      [ 59%]
tests/test_api.py::test_google_books_api_mocked PASSED                   [ 61%]
tests/test_gui.py::test_gui_views_initialization PASSED                  [ 63%]
tests/test_e2e.py::test_full_circulation_lifecycle PASSED               [100%]
============================== 47 passed in 30.80s ==============================
```

---

## 13. Limitations and Future Improvements

### Genuine Codebase Limitations:
1. **Single-Node SQLite Concurrency**: SQLite utilizes database-level locking during writes. For thousands of concurrent simultaneous loans, a client-server database like PostgreSQL would be preferred.
2. **Client-Side Session State**: The React app currently retains session status in browser `localStorage`.
3. **Public API Rate Limits**: Excessive rapid querying of the Google Books REST API can encounter HTTP 429 (Too Many Requests). The code handles this gracefully with an offline recommendations fallback.

### Realistic Future Improvements:
1. **Role-Based JWT Authentication**: Migrate to JSON Web Tokens with refresh cookies.
2. **Automated Overdue Email Reminders**: Integrate an SMTP mailer or Twilio WhatsApp API service.
3. **Physical Barcode / QR Scanner**: Support USB barcode scanners for instant ISBN checkout.
4. **Member Self-Service Mobile Portal**: Progressive Web App (PWA) allowing students to reserve books from their smartphones.

---

## 14. Review & Viva Voce Preparation

### 🎙️ 2-Minute Elevator Pitch (Memorize This)
> "Good morning, respected faculty. My project is the **Smart Library Management and Book Analytics System**. 
> It is an integrated full-stack application featuring a modern React 19 single-page application communicating with an asynchronous FastAPI REST API backend and an ACID-compliant SQLite database.
> The project comprehensively covers all five modules of our Advanced Python Programming syllabus:
> In **Module I**, I implemented clean OOP principles with an abstract `Person` class, `Member` and `Librarian` subclasses demonstrating inheritance and polymorphism, and operator overloading on the `Book` model for price sorting and stock summation.
> In **Module II**, I utilized functional programming techniques including `lambda`, `map`, `filter`, and `functools.reduce` for inventory valuations, along with set, dictionary, and list comprehensions, a custom iterator, and a role-based access control decorator.
> In **Module III**, I implemented concurrency benchmarks comparing single-thread sequential execution, `ThreadPoolExecutor`, and multi-core `multiprocessing.Pool`, demonstrating how multiprocessing overcomes the Python GIL.
> In **Module IV**, I used Pandas for categorical grouping and aggregations, and NumPy for statistical measures like mean, median, standard deviation, and percentiles, alongside regex validation and multi-format CSV, JSON, and XML handlers.
> In **Module V**, I developed the full-stack architecture with a FastAPI REST server, a responsive React frontend, and atomic database transactions for circulation loans, complete with live Google Books REST API integration.
> The entire backend is backed by 47 automated pytest test cases with 100% passing results."

---

### 🎙️ 5-Minute Detailed Demonstration Flow
1. **Introduction & Login (0:00 - 1:00)**:
   - Launch `run_backend.bat` and `run_frontend.bat`.
   - Open browser at `http://localhost:5173`.
   - Explain PBKDF2 password hashing. Click **"1-Click Quick Demo Sign In"**.
2. **Dashboard & KPIs (1:00 - 2:00)**:
   - Point out the 6 live KPI cards.
   - Show the Recharts Category Stock Bar Chart and Circulation Donut Chart.
   - Explain that all metrics are computed from SQLite records.
3. **Book Catalog & Functional Python Demo (2:00 - 3:00)**:
   - Navigate to `/books`. Show live search and category filtering.
   - Click the purple **"Module II: Functional Demo"** button.
   - Explain how `functools.reduce()` computes inventory valuation and how comprehensions extract categories.
4. **Circulation Atomic Transaction (3:00 - 4:00)**:
   - Navigate to `/loans`. Click **"Issue / Checkout Book"**.
   - Issue a book to a member. Show that available copies decrement automatically.
   - Switch to the "Overdue Loans" tab and explain the ₹2.00/day fine calculation.
   - Click **"Return"** on a book and demonstrate that stock is restored.
5. **Pandas/NumPy Analytics & Concurrency Lab (4:00 - 5:00)**:
   - Navigate to `/analytics`. Show the Pandas GroupBy table and NumPy statistical metrics (mean, median, percentiles).
   - Navigate to `/concurrency`. Click **"Run Live Benchmark"**.
   - Show the execution time chart and explain why multiprocessing achieved a multi-fold speedup over threading due to Python's GIL.
   - Conclude by highlighting the 47 automated tests passing in `pytest`.

---

### ❓ 25 Likely Viva Questions & Answers

#### Architecture & Stack
**Q1: What is the overall architecture of your system?**  
*Answer*: It is a decoupled multi-tier architecture: a React 19 SPA frontend communicates over asynchronous HTTP REST calls with a FastAPI backend server, which invokes Python business services, repositories, and an SQLite database.

**Q2: Why did you choose FastAPI instead of Flask or Django?**  
*Answer*: FastAPI is built on modern ASGI standards (`Starlette`), provides automatic request data validation through Pydantic schemas, delivers asynchronous non-blocking performance, and generates interactive Swagger API documentation out of the box.

**Q3: How does React communicate with the Python backend?**  
*Answer*: React uses an Axios HTTP client configured in `frontend/src/api/client.js`. During development, Vite's reverse proxy routes `/api` calls directly to `http://127.0.0.1:8000`, returning JSON payloads.

---

#### Object-Oriented Programming (Module I)
**Q4: How did you implement inheritance and polymorphism in your models?**  
*Answer*: In `models/person.py`, I created an abstract base class `Person`. Both `Member` (`models/member.py`) and `Librarian` (`models/librarian.py`) inherit from `Person` and polymorphically override the abstract method `get_role_display()`.

**Q5: What operator overloading did you implement?**  
*Answer*: In `models/book.py`, I overloaded the `<` operator (`__lt__`) to sort books by price, and the `+` operator (`__add__`) to aggregate the physical stock copies of identical books.

**Q6: Why did you implement `__bool__` on your `Book` class?**  
*Answer*: Because `__len__` is implemented to return available copies. In Python, an object with `len() == 0` evaluates to `False` in boolean conditions like `if book:`. Defining `def __bool__(self): return True` ensures books with zero stock are still recognized as existing objects.

---

#### Functional Programming (Module II)
**Q7: Where did you use `functools.reduce`?**  
*Answer*: In `services/book_service.py` in `calculate_total_inventory_valuation()`, where `reduce(lambda acc, b: acc + (b.price * b.total_copies), catalog, 0.0)` accumulates the total financial valuation of the entire catalog.

**Q8: Explain the difference between your Generator and Custom Iterator.**  
*Answer*: In `services/book_service.py`, `CatalogIterator` is a class implementing the iterator protocol (`__iter__` and `__next__`), while `stream_books_generator()` is a generator function utilizing Python's `yield` keyword to stream books in memory-conserving batches.

**Q9: Where have you used a Python Decorator?**  
*Answer*: In `services/auth_service.py`, I created the `@require_librarian` decorator using `functools.wraps` to inspect the caller's session and raise a `PermissionError` if an unprivileged user attempts administrative actions.

---

#### Concurrency & Performance (Module III)
**Q10: What is the Python GIL, and how does your project demonstrate it?**  
*Answer*: The Global Interpreter Lock (GIL) is a mutex in CPython that prevents multiple native threads from executing Python bytecodes simultaneously. In `concurrency/performance.py`, my CPU-bound Monte Carlo simulation shows that `ThreadPoolExecutor` cannot achieve linear speedup due to thread contention, whereas `multiprocessing.Pool` spawns independent processes with separate GILs, achieving true multi-core parallel speedup.

**Q11: Why use `time.perf_counter()` instead of `time.time()`?**  
*Answer*: `time.perf_counter()` is a high-resolution, monotonic clock that cannot go backwards due to system time adjustments, making it the standard choice for benchmarking code execution duration.

**Q12: Where is AsyncIO used in your project?**  
*Answer*: In `concurrency/async_tasks.py` and `api/google_books.py`, where asynchronous coroutines and `aiohttp` query external book endpoints concurrently without blocking the main event loop.

---

#### Data Handling & Analytics (Module IV)
**Q13: How does Pandas process your library data?**  
*Answer*: In `analytics/data_processor.py`, `load_books_dataframe()` loads SQL rows into a Pandas DataFrame. It calculates row-level valuations (`price * total_copies`) and uses `df.groupby("category").agg(...)` to compute stock sums and average prices per genre.

**Q14: What NumPy statistical calculations did you perform?**  
*Answer*: In `analytics/data_processor.py`, I converted book prices to a NumPy array (`df['price'].to_numpy()`) and computed `np.mean()`, `np.median()`, `np.std()`, `np.min()`, `np.max()`, and 25th/75th percentiles via `np.percentile()`.

**Q15: What regular expressions did you write?**  
*Answer*: In `utils/validators.py`, I used compiled regular expressions for validating Book IDs (`^BK-\d{3,6}$`), Member IDs (`^MEM-\d{3,6}$`), emails (`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`), and 10-digit phone numbers with optional `+91` country codes.

**Q16: Which structured data file formats can your application import and export?**  
*Answer*: It supports **CSV**, **JSON**, and **XML**, implemented using Python's standard `csv`, `json`, and `xml.etree.ElementTree` modules in `utils/file_handlers.py`.

---

#### Database & Transactions (Module V)
**Q17: How do you prevent inventory discrepancies when issuing a book?**  
*Answer*: In `database/repositories.py::issue_book_transaction()`, the insert into `loans` and the decrement of `available_copies` in `books` are executed inside a single SQLite transaction context (`with conn:`). If any statement fails, the entire transaction rolls back.

**Q18: What happens if a librarian tries to delete a book that is currently borrowed?**  
*Answer*: The database enforces `FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE RESTRICT`. SQLite raises an `IntegrityError`, which the service intercepts and returns as a descriptive error message stating that books with circulation history cannot be deleted.

**Q19: What borrowing business rules does your application enforce?**  
*Answer*:
1. Standard loan duration of 14 days.
2. Maximum borrowing quota of 5 active loans per member.
3. Rejection of checkouts when available physical stock is 0.
4. Overdue fines accruing at ₹2.00 per day past the due date.

---

#### Security & Quality Assurance
**Q20: How are passwords stored in your system?**  
*Answer*: Using salted `PBKDF2-HMAC-SHA256` hashing with 100,000 iterations and a cryptographically secure 16-byte salt generated via `os.urandom(16)`. No plaintext passwords exist in the database.

**Q21: How do you prevent SQL injection?**  
*Answer*: All database queries in `database/repositories.py` use parameterized queries with `?` placeholders; string concatenation is strictly prohibited.

**Q22: How many tests do you have and what do they verify?**  
*Answer*: I have 47 automated tests written in `pytest` spanning domain entities, functional pipelines, quota limits, transactions, Pandas/NumPy calculations, Google Books API mocks, and FastAPI REST endpoints. All 47 tests pass.

**Q23: What is the difference between your React frontend and the Tkinter GUI?**  
*Answer*: The React frontend is a modern web single-page application with responsive charts and client-side routing. The Tkinter GUI is a native desktop application with embedded Matplotlib canvases, preserved to demonstrate desktop GUI development for Module V.

**Q24: What external API did you integrate?**  
*Answer*: The Google Books REST API (`https://www.googleapis.com/books/v1/volumes`). It allows searching public book volumes and importing them directly into our local SQLite catalog with custom pricing and copy counts.

**Q25: What is your offline fallback strategy for the Google Books API?**  
*Answer*: In `api/google_books.py`, if the API request times out or encounters network failure or HTTP 429 rate limits, it catches the exception and returns a curated set of local book recommendations so the user interface never crashes.

---

## 15. Quick Revision & Demo Checklist

### ⚡ One-Line Tech Summary
- **FastAPI**: Asynchronous web backend exposing REST endpoints with Pydantic validation.
- **React 19**: Responsive frontend user interface with client-side routing.
- **SQLite**: Local ACID relational database with foreign keys and check constraints.
- **Pandas**: Used for category aggregation and DataFrame business calculations.
- **NumPy**: Used for price and loan duration statistical metrics (mean, median, percentiles).
- **Multiprocessing**: Bypasses the Python GIL to accelerate heavy numerical benchmarks across CPU cores.
- **PBKDF2**: Hashing algorithm ensuring passwords are encrypted with salted iterations.

### 🔑 Key Files to Remember
1. `api_server.py`: Launcher script for FastAPI.
2. `server/app.py`: FastAPI app instance and router configuration.
3. `services/book_service.py`: Functional programming (`reduce`, `map`, `filter`, comprehensions, iterator).
4. `services/loan_service.py`: Issue and return circulation rules and fine calculations.
5. `database/repositories.py`: SQLite parameterized queries and atomic transactions.
6. `analytics/data_processor.py`: Pandas and NumPy data analysis methods.
7. `concurrency/performance.py`: Sequential vs Threading vs Multiprocessing benchmark.
8. `frontend/src/App.jsx`: React routing and protected layout configuration.

### 📋 10-Point Pre-Demo Checklist
- [ ] Terminal 1: Backend running via `python api_server.py` on `http://127.0.0.1:8000`.
- [ ] Terminal 2: Frontend running via `npm run dev` on `http://localhost:5173`.
- [ ] Test the login page: `admin` / `admin123`.
- [ ] Check that Dashboard KPI cards and Recharts are visible.
- [ ] Open `/books` and show the "Module II: Functional Demo" modal.
- [ ] Open `/loans` and demonstrate issuing a book and returning a book.
- [ ] Open `/analytics` and demonstrate the Pandas table and NumPy price statistics cards.
- [ ] Open `/discovery` and perform a live Google Books search (e.g., "Machine Learning").
- [ ] Open `/concurrency` and run the parallel benchmark demonstrating multi-core speedup.
- [ ] Have a third terminal ready to run `pytest -v` to prove that all 47 tests pass.
