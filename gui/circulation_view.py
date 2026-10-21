"""Circulation Management View handling book issues, returns, and overdue loan monitoring."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime
from typing import Optional, Callable
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from services.loan_service import LoanService
from services.book_service import BookService
from services.member_service import MemberService
from config import THEME_COLORS, DEFAULT_LOAN_DAYS, DEFAULT_FINE_PER_DAY
from gui.styles import UIStyleHelper
from utils.logging_config import get_logger

logger = get_logger("gui.circulation_view")


class IssueBookDialog(tk.Toplevel):
    """Modal dialog for issuing a book with real-time stock and member check."""

    def __init__(
        self,
        parent: tk.Widget,
        book_service: BookService,
        member_service: MemberService,
        loan_service: LoanService,
        on_success: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.title("Issue Book to Member")
        self.geometry("520x460")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.book_service = book_service
        self.member_service = member_service
        self.loan_service = loan_service
        self.on_success = on_success

        self.configure(bg=THEME_COLORS["card_bg"])
        self._build_ui()

    def _build_ui(self) -> None:
        pad_x = 24
        self.columnconfigure(1, weight=1)

        hdr = tk.Label(
            self,
            text="Issue Book Workflow",
            font=UIStyleHelper.FONT_HEADER,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["primary"]
        )
        hdr.grid(row=0, column=0, columnspan=2, padx=pad_x, pady=(20, 16), sticky="w")

        # 1. Select Member
        tk.Label(self, text="Select Member:", font=UIStyleHelper.FONT_SUBHEADER, bg=THEME_COLORS["card_bg"]).grid(row=1, column=0, padx=pad_x, pady=6, sticky="w")
        self.member_combo = ttk.Combobox(self, state="readonly", font=UIStyleHelper.FONT_BODY)
        self.member_combo.grid(row=1, column=1, padx=pad_x, pady=6, sticky="ew")

        # 2. Select Book (Available only)
        tk.Label(self, text="Select Book:", font=UIStyleHelper.FONT_SUBHEADER, bg=THEME_COLORS["card_bg"]).grid(row=2, column=0, padx=pad_x, pady=6, sticky="w")
        self.book_combo = ttk.Combobox(self, state="readonly", font=UIStyleHelper.FONT_BODY)
        self.book_combo.grid(row=2, column=1, padx=pad_x, pady=6, sticky="ew")

        # 3. Loan Duration
        tk.Label(self, text="Loan Duration (Days):", font=UIStyleHelper.FONT_SUBHEADER, bg=THEME_COLORS["card_bg"]).grid(row=3, column=0, padx=pad_x, pady=6, sticky="w")
        self.days_entry = ttk.Entry(self, font=UIStyleHelper.FONT_BODY)
        self.days_entry.grid(row=3, column=1, padx=pad_x, pady=6, sticky="ew")
        self.days_entry.insert(0, str(DEFAULT_LOAN_DAYS))

        # 4. Info preview box
        self.preview_lbl = tk.Label(
            self,
            text="",
            font=UIStyleHelper.FONT_SMALL,
            bg="#F1F5F9",
            fg=THEME_COLORS["text_dark"],
            relief="solid",
            bd=1,
            padx=12,
            pady=10,
            justify="left"
        )
        self.preview_lbl.grid(row=4, column=0, columnspan=2, padx=pad_x, pady=16, sticky="ew")

        # Buttons
        btn_frame = tk.Frame(self, bg=THEME_COLORS["card_bg"])
        btn_frame.grid(row=5, column=0, columnspan=2, padx=pad_x, pady=(10, 20), sticky="e")

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(btn_frame, text="Confirm Issue", style="Success.TButton", command=self._submit_issue).pack(side="right")

        self._populate_dropdowns()
        self.book_combo.bind("<<ComboboxSelected>>", self._update_preview)
        self.member_combo.bind("<<ComboboxSelected>>", self._update_preview)

    def _populate_dropdowns(self) -> None:
        members = self.member_service.get_all_members()
        self.member_map = {f"{m.name} ({m.member_id})": m.member_id for m in members}
        self.member_combo["values"] = list(self.member_map.keys())
        if self.member_map:
            self.member_combo.current(0)

        # Module II: filter() used to present available books
        available_books = self.book_service.filter_available_books()
        self.book_map = {f"[{b.book_id}] {b.title} ({b.available_copies} avail)": b.book_id for b in available_books}
        self.book_combo["values"] = list(self.book_map.keys())
        if self.book_map:
            self.book_combo.current(0)
            self._update_preview()
        else:
            self.preview_lbl.config(text="⚠️ Notice: No books currently available in stock.")

    def _update_preview(self, event=None) -> None:
        b_key = self.book_combo.get()
        m_key = self.member_combo.get()
        b_id = self.book_map.get(b_key)
        m_id = self.member_map.get(m_key)

        if b_id and m_id:
            book = self.book_service.get_book(b_id)
            member = self.member_service.get_member(m_id)
            if book and member:
                self.preview_lbl.config(
                    text=f"Selected Book: {book.title} (ID: {book.book_id})\n"
                         f"Category: {book.category} | Available: {book.available_copies}/{book.total_copies}\n"
                         f"Borrower: {member.name} ({member.email})"
                )

    def _submit_issue(self) -> None:
        b_key = self.book_combo.get()
        m_key = self.member_combo.get()
        b_id = self.book_map.get(b_key)
        m_id = self.member_map.get(m_key)

        if not b_id or not m_id:
            messagebox.showerror("Error", "Please select both a valid member and book.", parent=self)
            return

        try:
            days = int(self.days_entry.get().strip())
            if days <= 0:
                raise ValueError("Loan duration must be at least 1 day.")
        except ValueError as ve:
            messagebox.showerror("Invalid Input", str(ve), parent=self)
            return

        try:
            loan_id = self.loan_service.issue_book(book_id=b_id, member_id=m_id, loan_days=days)
            messagebox.showinfo("Success", f"Book issued successfully!\nLoan Record ID: #{loan_id}", parent=self)
            if self.on_success:
                self.on_success()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Issue Failed", str(e), parent=self)


class CirculationView(ttk.Frame):
    """View managing active loans, return processing, and loan history."""

    def __init__(
        self,
        parent: tk.Widget,
        loan_service: LoanService,
        book_service: BookService,
        member_service: MemberService,
        on_data_changed: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.loan_service = loan_service
        self.book_service = book_service
        self.member_service = member_service
        self.on_data_changed = on_data_changed

        self.configure(style="TFrame")
        self._build_ui()
        self.load_loans()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        hdr = tk.Frame(self, bg=THEME_COLORS["content_bg"])
        hdr.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        title = tk.Label(hdr, text="Circulation Desk & Loans", font=UIStyleHelper.FONT_TITLE, bg=THEME_COLORS["content_bg"], fg=THEME_COLORS["text_dark"])
        title.pack(side="left")

        act_frame = tk.Frame(hdr, bg=THEME_COLORS["content_bg"])
        act_frame.pack(side="right")

        ttk.Button(act_frame, text="📖 Issue Book", style="Success.TButton", command=self._open_issue_dialog).pack(side="left", padx=4)
        ttk.Button(act_frame, text="↩️ Return Book", style="TButton", command=self._return_selected_loan).pack(side="left", padx=4)
        ttk.Button(act_frame, text="⚠️ Check Overdues", command=self._refresh_overdues).pack(side="left", padx=4)
        ttk.Button(act_frame, text="📤 Export", command=self._export_loans).pack(side="left", padx=4)

        # Tab Notebook: Active Loans vs All History
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=24, pady=(8, 20))

        # Tab 1: Active & Overdue
        self.active_tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.active_tab, text="Active & Overdue Loans")

        # Tab 2: Complete History
        self.history_tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.history_tab, text="All Circulation History")

        self._build_active_table(self.active_tab)
        self._build_history_table(self.history_tab)

        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.load_loans())

    def _build_active_table(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        cols = ("id", "book_id", "title", "member_id", "member_name", "issue_date", "due_date", "status", "fine")
        self.tree_active = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")

        self.tree_active.heading("id", text="Loan ID")
        self.tree_active.heading("book_id", text="Book ID")
        self.tree_active.heading("title", text="Book Title")
        self.tree_active.heading("member_id", text="Member ID")
        self.tree_active.heading("member_name", text="Borrower Name")
        self.tree_active.heading("issue_date", text="Issue Date")
        self.tree_active.heading("due_date", text="Due Date")
        self.tree_active.heading("status", text="Status")
        self.tree_active.heading("fine", text="Fine (₹)")

        self.tree_active.column("id", width=70, anchor="center")
        self.tree_active.column("book_id", width=85, anchor="center")
        self.tree_active.column("title", width=220, anchor="w")
        self.tree_active.column("member_id", width=95, anchor="center")
        self.tree_active.column("member_name", width=140, anchor="w")
        self.tree_active.column("issue_date", width=95, anchor="center")
        self.tree_active.column("due_date", width=95, anchor="center")
        self.tree_active.column("status", width=95, anchor="center")
        self.tree_active.column("fine", width=80, anchor="e")

        # Tags for overdue highlighting
        self.tree_active.tag_configure("OVERDUE", background="#FEE2E2", foreground="#991B1B")
        self.tree_active.tag_configure("ACTIVE", background="#FFFFFF")

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree_active.yview)
        self.tree_active.configure(yscrollcommand=vsb.set)

        self.tree_active.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

    def _build_history_table(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        cols = ("id", "book_id", "title", "member_id", "member_name", "issue_date", "due_date", "return_date", "status")
        self.tree_history = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")

        self.tree_history.heading("id", text="Loan ID")
        self.tree_history.heading("book_id", text="Book ID")
        self.tree_history.heading("title", text="Book Title")
        self.tree_history.heading("member_id", text="Member ID")
        self.tree_history.heading("member_name", text="Borrower Name")
        self.tree_history.heading("issue_date", text="Issue Date")
        self.tree_history.heading("due_date", text="Due Date")
        self.tree_history.heading("return_date", text="Returned Date")
        self.tree_history.heading("status", text="Status")

        self.tree_history.column("id", width=70, anchor="center")
        self.tree_history.column("book_id", width=85, anchor="center")
        self.tree_history.column("title", width=220, anchor="w")
        self.tree_history.column("member_id", width=95, anchor="center")
        self.tree_history.column("member_name", width=140, anchor="w")
        self.tree_history.column("issue_date", width=95, anchor="center")
        self.tree_history.column("due_date", width=95, anchor="center")
        self.tree_history.column("return_date", width=95, anchor="center")
        self.tree_history.column("status", width=95, anchor="center")

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree_history.yview)
        self.tree_history.configure(yscrollcommand=vsb.set)

        self.tree_history.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

    def load_loans(self) -> None:
        # Load active loans
        for item in self.tree_active.get_children():
            self.tree_active.delete(item)

        active = self.loan_service.get_active_loans()
        today = date.today()

        for l in active:
            is_overdue = False
            fine_str = "0.00"
            try:
                due = datetime.fromisoformat(l["due_date"]).date()
                if today > due:
                    is_overdue = True
                    days = (today - due).days
                    fine_str = f"{days * DEFAULT_FINE_PER_DAY:.2f}"
            except Exception:
                pass

            tag = "OVERDUE" if is_overdue or l["status"] == "OVERDUE" else "ACTIVE"
            status_display = "⚠️ OVERDUE" if tag == "OVERDUE" else "ACTIVE"

            self.tree_active.insert(
                "",
                "end",
                iid=str(l["loan_id"]),
                values=(
                    l["loan_id"],
                    l["book_id"],
                    l["title"],
                    l["member_id"],
                    l["member_name"],
                    l["issue_date"],
                    l["due_date"],
                    status_display,
                    fine_str
                ),
                tags=(tag,)
            )

        # Load complete history
        for item in self.tree_history.get_children():
            self.tree_history.delete(item)

        all_loans = self.loan_service.get_all_loans()
        for l in all_loans:
            self.tree_history.insert(
                "",
                "end",
                iid=f"hist_{l['loan_id']}",
                values=(
                    l["loan_id"],
                    l["book_id"],
                    l["title"],
                    l["member_id"],
                    l["member_name"],
                    l["issue_date"],
                    l["due_date"],
                    l["return_date"] or "—",
                    l["status"]
                )
            )

    def _open_issue_dialog(self) -> None:
        def on_done():
            self.load_loans()
            if self.on_data_changed:
                self.on_data_changed()

        IssueBookDialog(self, self.book_service, self.member_service, self.loan_service, on_success=on_done)

    def _return_selected_loan(self) -> None:
        sel = self.tree_active.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select an active loan to return.")
            return

        loan_id_str = sel[0]
        try:
            loan_id = int(loan_id_str)
        except ValueError:
            return

        confirm = messagebox.askyesno(
            "Confirm Return",
            f"Process return for Loan #{loan_id}?\n\nThis will atomically increment book shelf stock."
        )
        if not confirm:
            return

        try:
            self.loan_service.return_book(loan_id)
            self.load_loans()
            if self.on_data_changed:
                self.on_data_changed()
            messagebox.showinfo("Book Returned", f"Loan #{loan_id} marked as returned successfully.")
        except Exception as e:
            messagebox.showerror("Return Failed", str(e))

    def _refresh_overdues(self) -> None:
        overdues = self.loan_service.get_overdue_loans()
        self.load_loans()
        messagebox.showinfo("Overdue Check", f"Found {len(overdues)} overdue loan(s) currently past due date.")

    def _export_loans(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Export Circulation Records",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("JSON Files", "*.json")]
        )
        if not file_path:
            return

        fmt = "JSON" if file_path.endswith(".json") else "CSV"
        try:
            self.loan_service.export_loans(file_path, fmt)
            messagebox.showinfo("Export Success", f"Circulation records exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
