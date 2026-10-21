# Quality Assurance & Automated Test Plan

This document details the test strategy, automated test suites, test cases, and verified execution results for the **Smart Library Management and Book Analytics System**.

---

## 1. Test Strategy Overview

The testing architecture follows the standard test pyramid:
1. **Unit Tests**: Isolating domain models, cryptographic hashing, regular expression validation, functional programming pipelines, and file converters.
2. **Integration Tests**: Validating SQLite schema constraints, transactional integrity (foreign keys, non-negative stock counts), and mocked external REST API calls.
3. **End-to-End (E2E) Workflow Tests**: Simulating complete multi-step user scenarios from catalog creation to issuing, returning, and verifying analytical updates.
4. **GUI Smoke Tests**: Verifying that Tkinter views and modal dialogs instantiate and render without graphical or threading errors.

All automated tests utilize temporary isolated test databases (`tempfile.NamedTemporaryFile`) ensuring that the user's primary application data (`data/library.db`) is never modified or contaminated during testing.

---

## 2. Test Execution Summary

- **Test Runner**: `pytest` 9.1.1
- **Python Version**: 3.11.0 (64-bit)
- **Total Test Cases**: 38
- **Passed**: 38 (100%)
- **Failed**: 0
- **Execution Time**: ~13.00 seconds

---

## 3. Comprehensive Test Suite Matrix

| Module | Test Function Name | Tested Component | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **`tests/test_database.py`** | `test_tables_created` | DDL Schema (`schema.py`) | All core tables (`books`, `members`, `loans`, `librarians`) exist. | **PASSED** |
| | `test_foreign_key_enforcement` | SQLite Foreign Keys | Rejects orphan loan referencing non-existent book/member with `IntegrityError`. | **PASSED** |
| | `test_stock_constraint` | Check Constraint | Rejects book where `available_copies > total_copies` with `IntegrityError`. | **PASSED** |
| **`tests/test_validators.py`** | `test_valid_emails` | Regex (`utils/validators.py`) | Accepts valid emails; rejects invalid structures (`@no-user`, missing domain). | **PASSED** |
| | `test_valid_phones` | Regex (`utils/validators.py`) | Accepts 10-digit numbers & country codes; rejects alphabetic or short strings. | **PASSED** |
| | `test_valid_book_id` | Regex (`utils/validators.py`) | Validates alphanumeric IDs with hyphens; rejects invalid symbols. | **PASSED** |
| | `test_range_validator_closure`| Functional Closure | Validates values within dynamic boundaries defined in enclosing scope. | **PASSED** |
| | `test_validate_book_inputs` | Class Method Validation | Rejects negative prices and available stock exceeding total stock. | **PASSED** |
| **`tests/test_books.py`** | `test_book_model_encapsulation_and_operators` | Operator Overloading & Properties | Tests `<` sorting by available copies, `+` stock addition, and property guards. | **PASSED** |
| | `test_book_crud_lifecycle` | Book CRUD (`BookService`) | Verifies Add, Read, Update, and Safe Deletion of book entities. | **PASSED** |
| | `test_functional_programming_demonstrations` | Module II Functions | Verifies `filter()`, `map()`, `reduce()`, and list/set/dict comprehensions. | **PASSED** |
| | `test_generator_and_iterator` | Generator & Iterator | Verifies `stream_books_generator(batch_size)` and `CatalogIterator`. | **PASSED** |
| **`tests/test_members.py`** | `test_member_inheritance_and_polymorphism` | OOP Inheritance | Verifies `isinstance(m, Person)` and polymorphic `get_role_display()`. | **PASSED** |
| | `test_member_registration_and_search` | Member Registration | Adds member with regex check; rejects duplicate Member IDs. | **PASSED** |
| | `test_member_delete_safeguard` | Safe Deletion | Deletes unreferenced member cleanly. | **PASSED** |
| **`tests/test_loans.py`** | `test_normal_issue_and_return_workflow` | Issue & Return Transactions | Decrements available stock on issue; increments on return atomically. | **PASSED** |
| | `test_reject_issue_when_out_of_stock` | Stock Depletion Guard | Rejects issue attempt when available stock drops to 0. | **PASSED** |
| | `test_reject_duplicate_return` | Double Return Guard | Rejects duplicate return on already-returned loan with `ValueError`. | **PASSED** |
| | `test_reject_delete_when_active_or_historical_loans_exist` | Audit Integrity Guard | Blocks deletion of books or members associated with loan records. | **PASSED** |
| | `test_overdue_fine_calculation` | Overdue Policy | Calculates overdue days and assesses fine amount (`days * ₹2.0`). | **PASSED** |
| **`tests/test_api.py`** | `test_search_books_success` | Google Books API Client | Mocks HTTP 200 response and parses title, author, and ISBN correctly. | **PASSED** |
| | `test_search_books_timeout` | Network Timeout Guard | Mocks `requests.exceptions.Timeout` and raises `BookAPIError`. | **PASSED** |
| | `test_search_books_rate_limit`| Rate Limiting Guard | Mocks HTTP 429 response and raises user-friendly rate limit error. | **PASSED** |
| | `test_search_books_missing_fields` | Incomplete API Payloads | Robustly handles missing author/description without throwing KeyError. | **PASSED** |
| **`tests/test_analytics.py`** | `test_pandas_category_aggregation` | Pandas Aggregation | Aggregates titles, copies, and total valuation by category. | **PASSED** |
| | `test_numpy_price_statistics` | NumPy Statistical Engine | Calculates mean, median, standard deviation, and quartiles accurately. | **PASSED** |
| | `test_dashboard_summary_definitions`| Dashboard Metrics | Verifies conservation law: `total == available + issued`. | **PASSED** |
| | `test_visualization_figures_generated` | Matplotlib Charts | Generates valid bar chart, donut chart, and horizontal popular book charts. | **PASSED** |
| | `test_empty_dataset_handling` | Edge Case Robustness | Generates charts and metrics without crashing when tables are empty. | **PASSED** |
| **`tests/test_e2e.py`** | `test_complete_circulation_and_analytics_lifecycle` | End-to-End System Workflow | Verifies the complete 9-step college manual workflow end-to-end. | **PASSED** |
| **`tests/test_gui.py`** | `test_login_view_instantiation` | Login GUI View | Instantiates login card and radio options without GUI errors. | **PASSED** |
| | `test_dashboard_view_instantiation` | Dashboard GUI View | Renders summary cards and embedded Matplotlib figures. | **PASSED** |
| | `test_books_view_instantiation` | Books GUI View | Renders search filter bar, action buttons, and treeview table. | **PASSED** |
| | `test_members_view_instantiation` | Members GUI View | Renders member directory table and registration modals. | **PASSED** |
| | `test_circulation_view_instantiation` | Circulation Desk View | Renders dual notebook tabs and issue/return action handlers. | **PASSED** |
| | `test_analytics_view_instantiation` | Analytics GUI View | Renders 4 analytical notebook tabs and statistical tables. | **PASSED** |
| | `test_api_search_view_instantiation` | API Search GUI View | Renders search bar, preview pane, and background task worker. | **PASSED** |
| | `test_concurrency_view_instantiation`| Concurrency GUI View | Renders live CPU benchmark and AsyncIO testing controls. | **PASSED** |

---

## 4. End-to-End Workflow Verification

The end-to-end test in `tests/test_e2e.py` specifically verifies the exact sequential scenario mandated in Section 10 of the Master Prompt:
1. Initializes database service layer with clean tables.
2. Creates book `BK-E2E-101` with 3 total physical copies.
3. Registers member `MEM-E2E-201` (`Vikram Seth`).
4. Issues 1 copy of `BK-E2E-101` to `MEM-E2E-201`.
5. Asserts `available_copies` decreased to 2 and `issued_copies` became 1.
6. Returns the borrowed book.
7. Asserts `available_copies` returned to 3 and `issued_copies` became 0.
8. Asserts historical loan record is preserved with `status = 'RETURNED'` and valid return date.
9. Asserts Pandas DataFrame aggregations and NumPy price statistics accurately reflect final database records.
