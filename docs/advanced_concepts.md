# Advanced Python Programming — Course Concept Mapping

This document comprehensively maps every concept required across Modules I–V of the Advanced Python Programming syllabus to its exact implementation in the **Smart Library Management and Book Analytics System**.

---

## Module I: Object-Oriented Programming (OOP)

| Concept | File Location | Class / Function / Symbol | Practical Implementation Explanation |
| :--- | :--- | :--- | :--- |
| **Classes and Objects** | `models/person.py`<br>`models/book.py`<br>`models/loan.py` | `class Person`<br>`class Book`<br>`class Loan` | Models real-world domain entities representing library borrowers, physical/digital books, and circulation loan records. |
| **Constructors & Initialization** | `models/book.py:27`<br>`models/person.py:20` | `def __init__(self, ...)` | Initializes object state, setting default inventory counts, role flags, and triggering property setters for validation. |
| **Encapsulation** | `models/book.py:40-86`<br>`models/person.py:32-55` | `@property`<br>`@available_copies.setter`<br>`@price.setter` | Enforces private/protected fields (`_available_copies`, `_price`, `_email`). Prevents negative stock and ensures available copies never exceed total copies. |
| **Inheritance** | `models/member.py:10`<br>`models/librarian.py:15` | `class Member(Person)`<br>`class Librarian(Person)` | `Member` and `Librarian` inherit common identity attributes (`person_id`, `name`, `email`, `phone`) and methods from base `Person`. |
| **Polymorphism** | `models/person.py:61-68`<br>`models/member.py:32-40`<br>`models/librarian.py:53-68` | `get_role_display()`<br>`get_permissions()` | Subclasses override behavior: `Librarian` returns administrative permissions (`MANAGE_BOOKS`, `API_IMPORT`) while `Member` returns borrowing permissions. |
| **Method Overriding** | `models/member.py:33`<br>`models/librarian.py:54` | `def get_role_display(self)` | Specifically overrides base class `Person.get_role_display()` to return customized role titles ("Chief Librarian" or "Library Member / Student"). |
| **Special / Dunder Methods** | `models/person.py:80-87`<br>`models/book.py:126-143` | `__str__`, `__repr__`, `__eq__`, `__len__`, `__bool__` | `__str__` provides human-readable labels; `__eq__` compares entity identity; `__len__` returns available physical stock; `__bool__` returns truthiness. |
| **Instance Methods** | `models/book.py:96-107` | `issue_copy()`, `return_copy()` | Mutates instance state during circulation, decrementing or incrementing shelf stock while preserving boundary invariants. |
| **Class Method** | `models/book.py:165`<br>`models/librarian.py:91` | `@classmethod from_row()`<br>`@classmethod hash_password()` | Factory constructors instantiating domain models directly from SQLite `sqlite3.Row` results and generating cryptographically salted PBKDF2 hashes. |
| **Static Method** | `utils/validators.py:38-66`<br>`models/person.py:68` | `@staticmethod is_valid_email()`<br>`@staticmethod is_valid_phone()` | Stateless utility functions performing regex verification and format validation without requiring an instantiated class instance. |
| **Operator Overloading** | `models/book.py:109-135` | `__lt__` (less than `<`)<br>`__add__` (addition `+`) | `<` overloads comparison to sort books by available copies on shelf; `+` overloads addition to combine incoming physical shipments to stock. |

---

## Module II: Functional Programming and Iterators

| Concept | File Location | Class / Function / Symbol | Practical Implementation Explanation |
| :--- | :--- | :--- | :--- |
| **Lambda Expressions** | `services/book_service.py:122`<br>`services/book_service.py:128`<br>`services/book_service.py:137` | `lambda b: b.is_available`<br>`lambda b: f"[{b.book_id}] ..."`<br>`lambda acc, b: acc + ...` | Anonymous inline functions used for dynamic filtering, string formatting, and inventory valuation accumulation. |
| **map()** | `services/book_service.py:129` | `format_book_summaries()` | Transforms a collection of `Book` model instances into formatted catalog summary strings without mutating original objects. |
| **filter()** | `services/book_service.py:123` | `filter_available_books()` | Filters full catalog down to books that currently have at least one copy physically on the shelf (`available_copies > 0`). |
| **functools.reduce()** | `services/book_service.py:138` | `calculate_total_inventory_valuation()` | Aggregates and folds the monetary value (`price * total_copies`) of all books in the catalog into a single cumulative total valuation figure. |
| **List Comprehensions** | `services/book_service.py:157` | `get_low_stock_titles_list_comp()` | Pythonic filtering: `[b.title for b in catalog if b.available_copies <= threshold]`. |
| **Set Comprehensions** | `services/book_service.py:145` | `get_distinct_categories_set_comp()` | Extracts unique book categories into a set: `{b.category for b in catalog}`. |
| **Dictionary Comprehensions** | `services/book_service.py:151` | `get_stock_lookup_dict_comp()` | Builds a rapid dictionary lookup table: `{b.book_id: b.available_copies for b in catalog}`. |
| **Generator Functions** | `services/book_service.py:161-171` | `stream_books_generator(batch_size)` | Uses `yield` to stream book records in manageable chunks, reducing memory consumption for large catalogs. |
| **Custom Iterator / Iterable** | `services/book_service.py:18-35` | `class CatalogIterator` | Implements the iterator protocol using `__iter__()` and `__next__()` with `StopIteration` to traverse book collections sequentially. |
| **Custom Decorator** | `services/auth_service.py:18-33` | `@require_librarian` | Wraps sensitive administrative methods using `functools.wraps`, asserting user role permissions before executing protected functions. |
| **Higher-Order Function** | `services/book_service.py:177-183`<br>`utils/validators.py:21` | `filter_by_custom_predicate(predicate)`<br>`make_range_validator(...)` | Accepts a function as an argument (`predicate: Callable[[Book], bool]`) or returns a function dynamically configured with arguments. |
| **Closure** | `utils/validators.py:21-34` | `make_range_validator()` | Outer function captures `min_val`, `max_val`, and `field_name` in its lexical scope, returning an inner validator function retaining access to those closed variables. |

---

## Module III: Concurrency and Performance

| Concept | File Location | Class / Function / Symbol | Practical Implementation Explanation |
| :--- | :--- | :--- | :--- |
| **Multithreading** | `concurrency/background_tasks.py:23-53`<br>`gui/api_search_view.py:192` | `class BackgroundTaskWorker`<br>`threading.Thread` | Offloads I/O-bound operations (Google Books API queries, file imports/exports) to background threads, keeping Tkinter GUI at 60 FPS. |
| **Multiprocessing** | `concurrency/performance.py:22-38`<br>`concurrency/performance.py:93-112` | `heavy_risk_simulation_worker()`<br>`multiprocessing.Pool` | Distributes CPU-intensive Monte Carlo circulation risk simulations across OS processes, completely bypassing Python's GIL. |
| **AsyncIO** | `api/google_books.py:100-148`<br>`concurrency/async_tasks.py:15-38` | `async def search_books_async()`<br>`asyncio.gather()` | Executes non-blocking asynchronous HTTP network requests concurrently using `aiohttp` and an asynchronous event loop. |
| **Thread-Safe Queue & GUI Updates** | `concurrency/background_tasks.py:55-73` | `queue.Queue`<br>`root_tk.after(100, ...)` | Background worker threads push results to a thread-safe queue. The Tkinter main thread polls via `root.after()` so widgets are never modified off-thread. |
| **Performance Measurement** | `concurrency/performance.py:57, 72, 103` | `time.perf_counter()` | Captures microsecond-accurate benchmark timings to compare Sequential vs Multithreaded vs Multiprocessing performance. |
| **Documented Optimization** | `database/schema.py:46-55`<br>`analytics/data_processor.py:65` | SQLite B-Tree Indexes<br>NumPy Vectorization | Database indexes (`idx_books_category`, `idx_loans_status`) accelerate queries from $O(N)$ to $O(\log N)$; NumPy vectorized price calculations bypass Python loops. |
| **Assertions** | `concurrency/performance.py:118-120`<br>`tests/*.py` | `assert math.isclose(...)` | Asserts mathematical equivalence of parallel simulation outputs against single-threaded baselines. |
| **Profiling (cProfile)** | `concurrency/performance.py:133-145` | `cProfile.Profile()`<br>`pstats.Stats()` | Profiles function execution hotspots and cumulative call stack timings, viewable directly from the GUI. |

---

## Module IV: Libraries and Data Handling

| Concept | File Location | Class / Function / Symbol | Practical Implementation Explanation |
| :--- | :--- | :--- | :--- |
| **NumPy** | `analytics/data_processor.py:70-112` | `np.mean()`, `np.median()`, `np.std()`, `np.percentile()` | Computes comprehensive descriptive statistics and distribution quartiles for book prices and borrowing durations. |
| **Pandas** | `analytics/data_processor.py:24-65` | `pd.read_sql_query()`<br>`df.groupby().agg()` | Extracts relational tables into DataFrames, performing category aggregation, loan frequency counts, and borrowing trend analysis. |
| **Matplotlib in Tkinter** | `analytics/visualizations.py:24-125`<br>`gui/dashboard_view.py:118-135` | `FigureCanvasTkAgg`<br>`fig.add_subplot()` | Embeds dynamic interactive charts (Category Inventory Bar Chart, Circulation Status Donut Chart, Top Borrowed Books Chart) into Tkinter. |
| **Regular Expressions** | `utils/validators.py:14-18` | `re.compile()`<br>`EMAIL_REGEX`, `PHONE_REGEX`, `ISBN_REGEX` | Validates email syntax (`^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$`), 10-digit/E.164 phone numbers, and ISBN-10/13 formats. |
| **CSV Format** | `utils/file_handlers.py:20-37`<br>`utils/file_handlers.py:72-110` | `csv.DictWriter`<br>`csv.DictReader` | Reads and writes tabular book catalog and circulation records with field validation and header verification. |
| **JSON Format** | `utils/file_handlers.py:40-49`<br>`utils/file_handlers.py:112-149` | `json.dump()`, `json.load()` | Exports structured hierarchical data and imports book arrays with type validation and collision checks. |
| **XML Format** | `utils/file_handlers.py:51-69` | `xml.etree.ElementTree` | Generates formatted XML catalog trees (`<library_catalog><book>...`) as a third structured data format. |

---

## Module V: Application Development

| Concept | File Location | Class / Function / Symbol | Practical Implementation Explanation |
| :--- | :--- | :--- | :--- |
| **Functioning Desktop GUI** | `gui/main_window.py`<br>`gui/styles.py` | `class MainWindow(tk.Tk)`<br>`ttk.Style` | Complete desktop application featuring sidebar navigation, live statistic cards, data tables, dialog modals, and status indicators. |
| **REST API Consumption** | `api/google_books.py:47-98` | `class GoogleBooksAPI`<br>`requests.get()` | Queries Google Books REST API volumes endpoint, parses JSON payloads, handles rate limits (HTTP 429), and supports offline fallbacks. |
| **SQLite CRUD Operations** | `database/repositories.py:22-145` | `SELECT`, `INSERT`, `UPDATE`, `DELETE` | Full Create, Read, Update, Delete with parameterized SQL (`?`) protecting against SQL injection attacks. |
| **Data Integrity & Transactions** | `database/repositories.py:265-350` | `conn.commit()`, `conn.rollback()` | Atomic transaction boundaries: issuing a book decrements stock and creates loan; returning increments stock and updates status. |
| **End-to-End System Integration** | `main.py`<br>`tests/test_e2e.py` | Complete workflow | Connects GUI views, business services, SQLite database, REST API, Pandas analytics, and background workers into one cohesive micro-project. |
