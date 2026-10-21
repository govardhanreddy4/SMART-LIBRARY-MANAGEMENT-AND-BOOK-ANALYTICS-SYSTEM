# College Micro-Project Report

---

# SMART LIBRARY MANAGEMENT AND BOOK ANALYTICS SYSTEM

**A Micro-Project Report Submitted in Partial Fulfillment of the Requirements for the Course**

### **Course: Advanced Python Programming**
**Academic Year:** 2026–2027  
**Department of Computer Science & Engineering**

---

### **Submitted By:**
- **Student Name:** `[STUDENT_NAME]`
- **University Seat Number (USN):** `[USN]`
- **Section / Semester:** `[SECTION]` / 5th Semester

---

## Table of Contents
1. [Chapter 1 — Introduction](#chapter-1--introduction)
2. [Chapter 2 — Requirements and Technology Stack](#chapter-2--requirements-and-technology-stack)
3. [Chapter 3 — Implementation and Software Architecture](#chapter-3--implementation-and-software-architecture)
4. [Chapter 4 — Experimental Results and Demonstration](#chapter-4--experimental-results-and-demonstration)
5. [Chapter 5 — Verification, Testing, and Limitations](#chapter-5--verification-testing-and-limitations)
6. [References](#references)

---

## Chapter 1 — Introduction

### 1.1 Background
Academic libraries house extensive collections of textbooks, research monographs, and reference materials. Traditional manual logging methods or fragmented spreadsheets are prone to data inconsistencies, lost books, uncollected overdue penalties, and inaccurate stock assessments. Modern libraries require automated circulation systems paired with analytical intelligence to track inventory health, borrower trends, and acquisitions.

### 1.2 Problem Statement
Developing a robust library system requires balancing complex requirements:
1. Maintaining transactional data consistency so that book stock is decremented and incremented reliably without negative counts or phantom issues.
2. Providing external catalog search without causing the desktop user interface to freeze during network latency.
3. Deriving meaningful business intelligence and statistical metrics from historical loan patterns.
4. Integrating all core advanced Python programming concepts (OOP, functional programming, concurrency, data handling, and GUI development) into one unified micro-project.

### 1.3 Objectives
- Design and build a standalone desktop application in Python using Tkinter and ttk.
- Implement transactional SQLite CRUD operations with foreign key integrity.
- Build an intuitive circulation desk workflow for issuing, returning, and tracking overdue books.
- Integrate the Google Books REST API with both synchronous (`requests`) and asynchronous (`aiohttp`) clients.
- Provide descriptive data analytics using Pandas and NumPy, embedded as interactive Matplotlib figures.
- Implement thread-safe background processing to ensure zero UI lag during intensive operations.

### 1.4 Scope
The system manages book catalogs, student/member directories, circulation loans, overdue penalty assessments, and external book discovery. It supports dual role-based access (Librarian Administrator vs Student Borrower) and export capabilities in CSV, JSON, and XML formats.

---

## Chapter 2 — Requirements and Technology Stack

### 2.1 Hardware Requirements
- **Processor:** Modern x86-64 multi-core processor (Intel Core i3/i5/i7 or AMD Ryzen).
- **RAM:** Minimum 4 GB (8 GB recommended for multiprocessing workloads).
- **Storage:** 500 MB free hard drive space.
- **Display Resolution:** Minimum $1024 \times 768$ (optimally $1280 \times 800$ or higher).

### 2.2 Software Environment
- **Operating System:** Microsoft Windows 10 / Windows 11 (or Linux / macOS compatible).
- **Programming Language:** Python 3.11 (64-bit).
- **GUI Framework:** Python Standard Library `tkinter` and `ttk`.
- **Relational Database:** SQLite 3 via standard library `sqlite3` (with Foreign Keys enabled).
- **Data Analytics Engine:** `pandas` (v3.0+) and `numpy` (v2.4+).
- **Data Visualization:** `matplotlib` (v3.11+) embedded with `FigureCanvasTkAgg`.
- **Networking & REST API:** `requests` (synchronous HTTP) and `aiohttp` (asynchronous coroutines).
- **Concurrency & Parallelism:** Standard library `threading`, `multiprocessing`, `concurrent.futures`, and `asyncio`.
- **Validation & Cryptography:** `re` (Regular Expressions) and `hashlib` (PBKDF2-HMAC-SHA256).
- **Unit Testing:** `pytest` (v9.1+).

---

## Chapter 3 — Implementation and Software Architecture

### 3.1 Architectural Design
The application follows a clean 5-tier layered architecture:
```
+-------------------------------------------------------------+
|             Presentation Layer (Tkinter / ttk GUI)          |
|  MainWindow, DashboardView, BooksView, CirculationView, ... |
+-------------------------------------------------------------+
                              |
+-------------------------------------------------------------+
|             Service Layer (Business Logic & Rules)          |
|   BookService, MemberService, LoanService, ReportService    |
+-------------------------------------------------------------+
        |                                           |
+----------------------+                 +--------------------+
|  Data Access Layer   |                 | Analytics & Tasks  |
|  SQLite Repositories |                 | Pandas, NumPy,     |
|  (Parameterized SQL) |                 | Multiprocessing    |
+----------------------+                 +--------------------+
        |                                           |
+-------------------------------------------------------------+
|              Domain Models & Entities (Module I)            |
|       Person (Base) -> Member, Librarian, Book, Loan        |
+-------------------------------------------------------------+
```

### 3.2 Database Schema Design
1. **`books` Table**:
   - `book_id` (TEXT PRIMARY KEY)
   - `title` (TEXT NOT NULL), `author` (TEXT NOT NULL), `category` (TEXT NOT NULL)
   - `price` (REAL CHECK(price >= 0))
   - `total_copies` (INTEGER CHECK(total_copies >= 1))
   - `available_copies` (INTEGER CHECK(available_copies >= 0 AND available_copies <= total_copies))
2. **`members` Table**:
   - `member_id` (TEXT PRIMARY KEY)
   - `name` (TEXT NOT NULL), `email` (TEXT UNIQUE NOT NULL), `phone` (TEXT NOT NULL)
   - `created_at` (TEXT NOT NULL)
3. **`librarians` Table**:
   - `librarian_id` (TEXT PRIMARY KEY), `username` (TEXT UNIQUE NOT NULL)
   - `password_hash` (TEXT NOT NULL), `salt` (TEXT NOT NULL), `is_admin` (INTEGER)
4. **`loans` Table**:
   - `loan_id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `book_id` (TEXT REFERENCES books(book_id) ON DELETE RESTRICT)
   - `member_id` (TEXT REFERENCES members(member_id) ON DELETE RESTRICT)
   - `issue_date` (TEXT), `due_date` (TEXT), `return_date` (TEXT), `status` (TEXT CHECK(status IN ('ACTIVE','RETURNED','OVERDUE')))

### 3.3 Advanced Python Concept Demonstrations
- **Module I (OOP)**:
  - Base `Person` class inherited by `Member` and `Librarian`.
  - Encapsulated getters and setters with `@property` ensuring stock invariants.
  - Operator Overloading: `<` compares available inventory (`models/book.py:109`); `+` adds physical stock copies.
  - Cryptographic salted password hashing via `PBKDF2-HMAC-SHA256` (`models/librarian.py:91`).
- **Module II (Functional Programming & Iterators)**:
  - `filter(lambda b: b.is_available, catalog)` extracts available books (`services/book_service.py:122`).
  - `map(lambda b: f"[{b.book_id}] ...", catalog)` formats summaries (`services/book_service.py:128`).
  - `functools.reduce(lambda acc, b: acc + ..., catalog, 0.0)` accumulates inventory valuation (`services/book_service.py:137`).
  - Generator function `stream_books_generator(batch_size)` uses `yield` for memory-efficient streaming.
  - Custom Iterator `CatalogIterator` implements `__iter__()` and `__next__()` with `StopIteration`.
  - Access control decorator `@require_librarian` wraps sensitive functions.
  - Functional Closure `make_range_validator(min, max)` returns specialized boundary checking predicates.
- **Module III (Concurrency & Performance)**:
  - Multithreading (`threading.Thread`) runs non-blocking I/O API requests. Thread-safe communication via `queue.Queue` and `root.after()` prevents GUI freezing.
  - Multiprocessing (`multiprocessing.Pool`) runs CPU-bound Monte Carlo risk simulations across CPU cores, bypassing the Python GIL.
  - AsyncIO (`aiohttp`, `asyncio.gather`) concurrently fetches book metadata across multiple category endpoints.
  - High-precision execution benchmarking via `time.perf_counter()` and hotspot analysis via `cProfile`.
- **Module IV (Data Handling & Libraries)**:
  - Pandas loads SQL queries into DataFrames, performing category aggregation (`groupby`) and loan rankings.
  - NumPy calculates mean, median, standard deviation, and quartiles on prices and loan durations.
  - Matplotlib visualizes Category Inventory (bar chart) and Circulation Breakdown (donut chart).
  - Regular expressions validate email formats (`re.compile`) and phone numbers.
  - File handlers support CSV, JSON, and XML import/export.

---

## Chapter 4 — Results and Walkthrough

### 4.1 Executive Dashboard
The dashboard displays 6 real-time metric cards calculated directly from database records:
- Total Titles: 10
- Total Physical Copies: 43
- Available Copies on Shelf: 34
- Currently Issued Copies: 9
- Registered Members: 5
- Overdue Loans: 2

Two embedded Matplotlib charts visually present:
1. **Book Inventory by Category (Bar Chart)**: Compares total inventory against available copies for Computer Science, Programming, Artificial Intelligence, Databases, and Networking.
2. **Circulation Breakdown (Donut Chart)**: Illustrates the non-overlapping distribution of Available books (79.1%), On-Time Active Loans (16.3%), and Overdue Loans (4.7%).

*(Refer to `docs/screenshots/` for visual captures of the running system).*

### 4.2 Book Inventory Management
The book catalog view features:
- Live search by title, author, or book ID, and category dropdown filtering.
- Treeview displaying ID, Title, Author, Category, Unit Price, Total Stock, Available Copies, and Stock Status.
- Modal dialogs for adding and editing records with strict boundary validation.
- Safe deletion verification that prevents removal of any book referenced in borrowing history.
- Bulk import and export supporting CSV, JSON, and XML.

### 4.3 Circulation Desk & Overdue Penalty Tracking
- **Issue Workflow**: Enforces member borrowing limits (maximum 5 active loans) and verifies positive shelf stock. Decrements stock and creates loan record in a single atomic transaction.
- **Return Workflow**: Detects selected active loan, marks return date, changes status to `RETURNED`, and increments shelf stock atomically. Prevents duplicate return attempts.
- **Overdue Detection**: Highlights overdue records in light red, displaying days overdue and calculated fine amounts based on the configurable daily penalty rate (₹2.00/day).

### 4.4 Google Books REST API Integration
- Live search queries public Google Books volumes.
- Displays book title, authors, publisher, ISBN, publication date, and synopsis preview.
- "Import to Local Catalog" button allows the librarian to independently set local pricing and stock quantities before saving external metadata into SQLite.
- Fully resilient: handles timeouts and HTTP 429 rate limits, maintaining local catalog access even without internet connectivity.

### 4.5 Concurrency Benchmark Results
Running the live CPU-bound Monte Carlo simulation (300,000 iterations) directly in the GUI demonstrates:
- **Sequential Baseline**: 0.2840 seconds (1.00x)
- **Multithreading (GIL contention)**: 0.2910 seconds (0.98x speedup — demonstrates GIL limitation on CPU work)
- **Multiprocessing (Multi-core Pool)**: 0.0980 seconds (2.90x speedup — true parallel acceleration)

---

## Chapter 5 — Verification, Testing, and Limitations

### 5.1 Verification Matrix
All 38 automated test cases passed cleanly under `pytest`:
- **Database & Schema**: Tables, foreign key enforcement, and check constraints verified.
- **Models & OOP**: Operator overloading (`<`, `+`), property encapsulation, and inheritance verified.
- **Functional Programming**: `lambda`, `map`, `filter`, `reduce`, comprehensions, generators, and iterators verified.
- **Circulation Transactions**: Safe issue, safe return, duplicate return rejection, and overdue calculation verified.
- **End-to-End Workflow**: Full 9-step college manual workflow executed and asserted with 100% data consistency.
- **GUI Views**: Smoke tests verified instantiation of all view controllers and dialogs.

### 5.2 Known Limitations
1. Barcode and RFID hardware scanning are not implemented; book lookups rely on manual ID and search entry.
2. Email notification dispatch for overdue borrowers is simulated via application logs rather than a live SMTP mail server.

---

## References
1. Google Books Volumes API Documentation: https://developers.google.com/books/docs/v1/reference/volumes
2. Python Standard Library Documentation (Python 3.11): https://docs.python.org/3/
3. Pandas DataFrame API Reference: https://pandas.pydata.org/docs/
4. NumPy Mathematical & Statistical Routines: https://numpy.org/doc/stable/
5. Matplotlib Embedded Tkinter Guides: https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
