"""Book Management View with search, filter, CRUD dialogs, and file import/export."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from services.book_service import BookService
from models.book import Book
from config import THEME_COLORS
from gui.styles import UIStyleHelper
from utils.logging_config import get_logger

logger = get_logger("gui.books_view")


class BookFormDialog(tk.Toplevel):
    """Modal dialog for adding or editing a book entity."""

    def __init__(self, parent: tk.Widget, title: str, book: Optional[Book] = None, on_save: Optional[Callable[[dict], None]] = None):
        super().__init__(parent)
        self.title(title)
        self.geometry("480x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.book = book
        self.on_save = on_save
        self.configure(bg=THEME_COLORS["card_bg"])

        self._build_form()
        if book:
            self._populate_fields(book)

    def _build_form(self) -> None:
        pad_x = 24
        self.columnconfigure(1, weight=1)

        header = tk.Label(
            self,
            text="Book Details" if not self.book else f"Edit Book: {self.book.book_id}",
            font=UIStyleHelper.FONT_HEADER,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["primary"]
        )
        header.grid(row=0, column=0, columnspan=2, padx=pad_x, pady=(20, 16), sticky="w")

        fields = [
            ("Book ID:", "id_entry", False),
            ("Title:", "title_entry", False),
            ("Author:", "author_entry", False),
            ("Category:", "cat_entry", False),
            ("Price (₹):", "price_entry", False),
            ("Total Copies:", "total_entry", False),
            ("Available Copies:", "avail_entry", False),
        ]

        self.entries = {}
        for idx, (label_text, entry_attr, _) in enumerate(fields, start=1):
            lbl = tk.Label(self, text=label_text, font=UIStyleHelper.FONT_SUBHEADER, bg=THEME_COLORS["card_bg"], fg=THEME_COLORS["text_dark"])
            lbl.grid(row=idx, column=0, padx=pad_x, pady=6, sticky="w")

            ent = ttk.Entry(self, font=UIStyleHelper.FONT_BODY)
            ent.grid(row=idx, column=1, padx=pad_x, pady=6, sticky="ew")
            self.entries[entry_attr] = ent

        # If editing, lock book_id
        if self.book:
            self.entries["id_entry"].config(state="disabled")

        # Buttons
        btn_frame = tk.Frame(self, bg=THEME_COLORS["card_bg"])
        btn_frame.grid(row=len(fields) + 1, column=0, columnspan=2, padx=pad_x, pady=24, sticky="e")

        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="right", padx=(8, 0))

        save_btn = ttk.Button(btn_frame, text="Save Book", style="Success.TButton", command=self._submit)
        save_btn.pack(side="right")

    def _populate_fields(self, book: Book) -> None:
        self.entries["id_entry"].insert(0, book.book_id)
        self.entries["title_entry"].insert(0, book.title)
        self.entries["author_entry"].insert(0, book.author)
        self.entries["cat_entry"].insert(0, book.category)
        self.entries["price_entry"].insert(0, str(book.price))
        self.entries["total_entry"].insert(0, str(book.total_copies))
        self.entries["avail_entry"].insert(0, str(book.available_copies))

    def _submit(self) -> None:
        b_id = self.book.book_id if self.book else self.entries["id_entry"].get().strip()
        title = self.entries["title_entry"].get().strip()
        author = self.entries["author_entry"].get().strip()
        category = self.entries["cat_entry"].get().strip()
        price_str = self.entries["price_entry"].get().strip()
        total_str = self.entries["total_entry"].get().strip()
        avail_str = self.entries["avail_entry"].get().strip()

        try:
            price = float(price_str)
            total = int(total_str)
            avail = int(avail_str) if avail_str else total
        except ValueError:
            messagebox.showerror("Validation Error", "Price must be numeric and copies must be valid integers.", parent=self)
            return

        data = {
            "book_id": b_id,
            "title": title,
            "author": author,
            "category": category,
            "price": price,
            "total_copies": total,
            "available_copies": avail
        }

        if self.on_save:
            self.on_save(data)
        self.destroy()


class BooksView(ttk.Frame):
    """Complete book catalog management interface."""

    def __init__(self, parent: tk.Widget, book_service: BookService, on_data_changed: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.book_service = book_service
        self.on_data_changed = on_data_changed

        self.configure(style="TFrame")
        self._build_ui()
        self.load_books()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Header Bar
        hdr = tk.Frame(self, bg=THEME_COLORS["content_bg"])
        hdr.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        title = tk.Label(hdr, text="Book Inventory & Catalog", font=UIStyleHelper.FONT_TITLE, bg=THEME_COLORS["content_bg"], fg=THEME_COLORS["text_dark"])
        title.pack(side="left")

        # Action Buttons on right
        act_frame = tk.Frame(hdr, bg=THEME_COLORS["content_bg"])
        act_frame.pack(side="right")

        ttk.Button(act_frame, text="➕ Add Book", style="Success.TButton", command=self._open_add_dialog).pack(side="left", padx=4)
        ttk.Button(act_frame, text="✏️ Edit", command=self._open_edit_dialog).pack(side="left", padx=4)
        ttk.Button(act_frame, text="🗑️ Delete", style="Danger.TButton", command=self._delete_selected_book).pack(side="left", padx=4)
        ttk.Button(act_frame, text="📥 Import", command=self._import_books).pack(side="left", padx=4)
        ttk.Button(act_frame, text="📤 Export", command=self._export_books).pack(side="left", padx=4)

        # Search and Filtering Filter Bar
        filter_bar = tk.Frame(self, bg=THEME_COLORS["card_bg"], padx=16, pady=10, relief="solid", bd=1)
        filter_bar.grid(row=1, column=0, sticky="ew", padx=24, pady=8)

        tk.Label(filter_bar, text="Search:", font=UIStyleHelper.FONT_SUBHEADER, bg=THEME_COLORS["card_bg"]).pack(side="left", padx=(0, 6))
        self.search_entry = ttk.Entry(filter_bar, width=28)
        self.search_entry.pack(side="left", padx=(0, 14))
        self.search_entry.bind("<Return>", lambda e: self.load_books())

        tk.Label(filter_bar, text="Category:", font=UIStyleHelper.FONT_SUBHEADER, bg=THEME_COLORS["card_bg"]).pack(side="left", padx=(0, 6))
        self.cat_combo = ttk.Combobox(filter_bar, values=["All Categories"], state="readonly", width=20)
        self.cat_combo.set("All Categories")
        self.cat_combo.pack(side="left", padx=(0, 14))
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.load_books())

        ttk.Button(filter_bar, text="🔍 Search", command=self.load_books).pack(side="left", padx=4)
        ttk.Button(filter_bar, text="Reset", command=self._reset_search).pack(side="left", padx=4)

        # Data Table (Treeview)
        table_frame = tk.Frame(self, bg=THEME_COLORS["card_bg"], bd=1, relief="solid")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=24, pady=(8, 20))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("id", "title", "author", "category", "price", "total", "avail", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="Book ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("author", text="Author")
        self.tree.heading("category", text="Category")
        self.tree.heading("price", text="Price (₹)")
        self.tree.heading("total", text="Total Stock")
        self.tree.heading("avail", text="Available")
        self.tree.heading("status", text="Stock Status")

        self.tree.column("id", width=90, anchor="center")
        self.tree.column("title", width=260, anchor="w")
        self.tree.column("author", width=160, anchor="w")
        self.tree.column("category", width=140, anchor="center")
        self.tree.column("price", width=80, anchor="e")
        self.tree.column("total", width=80, anchor="center")
        self.tree.column("avail", width=80, anchor="center")
        self.tree.column("status", width=100, anchor="center")

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<Double-1>", lambda e: self._open_edit_dialog())

    def _refresh_categories(self) -> None:
        """Update category filter values."""
        cats = ["All Categories"] + self.book_service.get_categories()
        current = self.cat_combo.get()
        self.cat_combo["values"] = cats
        if current in cats:
            self.cat_combo.set(current)
        else:
            self.cat_combo.set("All Categories")

    def load_books(self) -> None:
        """Fetch books according to current search criteria."""
        query = self.search_entry.get().strip()
        cat = self.cat_combo.get()
        books = self.book_service.search_books(query, cat)

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        for b in books:
            status_text = "In Stock" if b.is_available else "Out of Stock"
            self.tree.insert(
                "",
                "end",
                iid=b.book_id,
                values=(
                    b.book_id,
                    b.title,
                    b.author,
                    b.category,
                    f"{b.price:.2f}",
                    b.total_copies,
                    b.available_copies,
                    status_text
                )
            )
        self._refresh_categories()

    def _reset_search(self) -> None:
        self.search_entry.delete(0, tk.END)
        self.cat_combo.set("All Categories")
        self.load_books()

    def _open_add_dialog(self) -> None:
        def on_save(data):
            try:
                self.book_service.add_book(**data)
                self.load_books()
                if self.on_data_changed:
                    self.on_data_changed()
                messagebox.showinfo("Success", f"Book '{data['title']}' added successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add book: {e}")

        BookFormDialog(self, title="Add New Book", book=None, on_save=on_save)

    def _open_edit_dialog(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a book to edit.")
            return

        b_id = sel[0]
        book = self.book_service.get_book(b_id)
        if not book:
            messagebox.showerror("Error", "Book not found.")
            return

        def on_save(data):
            try:
                self.book_service.update_book(**data)
                self.load_books()
                if self.on_data_changed:
                    self.on_data_changed()
                messagebox.showinfo("Success", f"Book '{data['book_id']}' updated successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not update book: {e}")

        BookFormDialog(self, title="Edit Book", book=book, on_save=on_save)

    def _delete_selected_book(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a book to delete.")
            return

        b_id = sel[0]
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete book '{b_id}'?\n\nThis cannot be undone."
        )
        if not confirm:
            return

        try:
            self.book_service.delete_book(b_id)
            self.load_books()
            if self.on_data_changed:
                self.on_data_changed()
            messagebox.showinfo("Deleted", f"Book '{b_id}' deleted successfully.")
        except Exception as e:
            messagebox.showerror("Cannot Delete", str(e))

    def _import_books(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Import Books",
            filetypes=[("Supported Files", "*.csv;*.json"), ("CSV Files", "*.csv"), ("JSON Files", "*.json")]
        )
        if not file_path:
            return

        fmt = "CSV" if file_path.endswith(".csv") else "JSON"
        try:
            res = self.book_service.import_catalog(file_path, fmt)
            msg = f"Import Completed!\n\nImported: {res['imported']}\nSkipped: {res['skipped']}"
            if res['errors']:
                msg += f"\n\nWarnings/Errors:\n" + "\n".join(res['errors'][:5])
            messagebox.showinfo("Import Summary", msg)
            self.load_books()
            if self.on_data_changed:
                self.on_data_changed()
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import file: {e}")

    def _export_books(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Export Catalog",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("JSON Files", "*.json"), ("XML Files", "*.xml")]
        )
        if not file_path:
            return

        if file_path.endswith(".json"):
            fmt = "JSON"
        elif file_path.endswith(".xml"):
            fmt = "XML"
        else:
            fmt = "CSV"

        try:
            self.book_service.export_catalog(file_path, fmt)
            messagebox.showinfo("Export Success", f"Catalog successfully exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export catalog: {e}")
