"""Google Books REST API Search View with async/threaded background fetching."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api.google_books import GoogleBooksAPI, BookAPIError
from services.book_service import BookService
from concurrency.background_tasks import BackgroundTaskWorker
from config import THEME_COLORS
from gui.styles import UIStyleHelper
from utils.logging_config import get_logger

logger = get_logger("gui.api_search_view")


class ExternalBookImportDialog(tk.Toplevel):
    """Modal dialog allowing librarian to customize local pricing and copies before importing."""

    def __init__(self, parent: tk.Widget, book_data: Dict[str, Any], on_import_confirmed: Callable[[dict], None]):
        super().__init__(parent)
        self.title("Import Book to Local Catalog")
        self.geometry("480x480")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.book_data = book_data
        self.on_import_confirmed = on_import_confirmed
        self.configure(bg=THEME_COLORS["card_bg"])

        self._build_ui()

    def _build_ui(self) -> None:
        pad_x = 24
        self.columnconfigure(1, weight=1)

        hdr = tk.Label(
            self,
            text="Catalog Import Settings",
            font=UIStyleHelper.FONT_HEADER,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["primary"]
        )
        hdr.grid(row=0, column=0, columnspan=2, padx=pad_x, pady=(20, 14), sticky="w")

        info_box = tk.Label(
            self,
            text=f"Title: {self.book_data['title']}\n"
                 f"Author: {self.book_data['author']}\n"
                 f"Publisher: {self.book_data['publisher']} ({self.book_data['published_date']})\n"
                 f"ISBN: {self.book_data['isbn'] or 'N/A'}",
            font=UIStyleHelper.FONT_SMALL,
            bg="#F8FAFC",
            fg=THEME_COLORS["text_dark"],
            relief="solid",
            bd=1,
            padx=12,
            pady=10,
            justify="left"
        )
        info_box.grid(row=1, column=0, columnspan=2, padx=pad_x, pady=(0, 16), sticky="ew")

        # Custom Local Inputs
        fields = [
            ("Local Book ID:", "id_ent", self.book_data["suggested_book_id"]),
            ("Category:", "cat_ent", self.book_data["category"] or "General"),
            ("Local Unit Price (₹):", "price_ent", "500.0"),
            ("Physical Copies to Add:", "copies_ent", "3"),
        ]

        self.entries = {}
        for idx, (label_text, attr, default_val) in enumerate(fields, start=2):
            lbl = tk.Label(self, text=label_text, font=UIStyleHelper.FONT_SUBHEADER, bg=THEME_COLORS["card_bg"], fg=THEME_COLORS["text_dark"])
            lbl.grid(row=idx, column=0, padx=pad_x, pady=6, sticky="w")

            ent = ttk.Entry(self, font=UIStyleHelper.FONT_BODY)
            ent.grid(row=idx, column=1, padx=pad_x, pady=6, sticky="ew")
            ent.insert(0, default_val)
            self.entries[attr] = ent

        btn_frame = tk.Frame(self, bg=THEME_COLORS["card_bg"])
        btn_frame.grid(row=len(fields) + 3, column=0, columnspan=2, padx=pad_x, pady=24, sticky="e")

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(btn_frame, text="Confirm Import", style="Success.TButton", command=self._submit).pack(side="right")

    def _submit(self) -> None:
        b_id = self.entries["id_ent"].get().strip()
        cat = self.entries["cat_ent"].get().strip()
        try:
            price = float(self.entries["price_ent"].get().strip())
            copies = int(self.entries["copies_ent"].get().strip())
            if price < 0 or copies <= 0:
                raise ValueError("Price must be positive and copies at least 1.")
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e), parent=self)
            return

        import_payload = {
            "book_id": b_id,
            "title": self.book_data["title"],
            "author": self.book_data["author"],
            "category": cat,
            "price": price,
            "total_copies": copies,
            "available_copies": copies
        }
        self.on_import_confirmed(import_payload)
        self.destroy()


class APISearchView(ttk.Frame):
    """View consuming the Google Books REST API with responsive threading and UI queues."""

    def __init__(
        self,
        parent: tk.Widget,
        book_service: BookService,
        task_worker: BackgroundTaskWorker,
        on_data_changed: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.book_service = book_service
        self.task_worker = task_worker
        self.on_data_changed = on_data_changed
        self.api = GoogleBooksAPI()

        self.current_results: List[Dict[str, Any]] = []

        self.configure(style="TFrame")
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Header Frame
        hdr = tk.Frame(self, bg=THEME_COLORS["content_bg"])
        hdr.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        title = tk.Label(
            hdr,
            text="Google Books Discovery & Catalog Import (REST API)",
            font=UIStyleHelper.FONT_TITLE,
            bg=THEME_COLORS["content_bg"],
            fg=THEME_COLORS["text_dark"]
        )
        title.pack(side="left")

        # Search Bar
        search_bar = tk.Frame(self, bg=THEME_COLORS["card_bg"], padx=16, pady=12, relief="solid", bd=1)
        search_bar.grid(row=1, column=0, sticky="ew", padx=24, pady=8)

        tk.Label(
            search_bar,
            text="Query (Title, Author, or ISBN):",
            font=UIStyleHelper.FONT_SUBHEADER,
            bg=THEME_COLORS["card_bg"]
        ).pack(side="left", padx=(0, 10))

        self.search_ent = ttk.Entry(search_bar, width=38)
        self.search_ent.pack(side="left", padx=(0, 10))
        self.search_ent.insert(0, "Python Programming")
        self.search_ent.bind("<Return>", lambda e: self._start_search())

        self.search_btn = ttk.Button(search_bar, text="🔍 Search Online", style="TButton", command=self._start_search)
        self.search_btn.pack(side="left", padx=4)

        self.status_lbl = tk.Label(
            search_bar,
            text="Ready to search Google Books API.",
            font=UIStyleHelper.FONT_SMALL,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["text_muted"]
        )
        self.status_lbl.pack(side="left", padx=16)

        # Main Split Frame: Left Treeview Results, Right Book Details Panel
        split_frame = tk.Frame(self, bg=THEME_COLORS["content_bg"])
        split_frame.grid(row=2, column=0, sticky="nsew", padx=24, pady=(8, 20))
        split_frame.columnconfigure(0, weight=3)
        split_frame.columnconfigure(1, weight=2)
        split_frame.rowconfigure(0, weight=1)

        # Left Table
        tbl_frame = tk.Frame(split_frame, bg=THEME_COLORS["card_bg"], bd=1, relief="solid")
        tbl_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tbl_frame.columnconfigure(0, weight=1)
        tbl_frame.rowconfigure(0, weight=1)

        cols = ("title", "author", "category", "publisher", "isbn")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("title", text="Book Title")
        self.tree.heading("author", text="Author(s)")
        self.tree.heading("category", text="Category")
        self.tree.heading("publisher", text="Publisher")
        self.tree.heading("isbn", text="ISBN")

        self.tree.column("title", width=220, anchor="w")
        self.tree.column("author", width=140, anchor="w")
        self.tree.column("category", width=110, anchor="center")
        self.tree.column("publisher", width=120, anchor="w")
        self.tree.column("isbn", width=110, anchor="center")

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self._on_select_item)

        # Right Detail & Import Card
        self.detail_card = tk.Frame(split_frame, bg=THEME_COLORS["card_bg"], bd=1, relief="solid", padx=16, pady=16)
        self.detail_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(
            self.detail_card,
            text="Selected Book Preview",
            font=UIStyleHelper.FONT_HEADER,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["primary"]
        ).pack(anchor="w", pady=(0, 10))

        self.preview_text = tk.Text(
            self.detail_card,
            wrap="word",
            font=UIStyleHelper.FONT_BODY,
            bg="#F8FAFC",
            relief="flat",
            height=14
        )
        self.preview_text.pack(fill="both", expand=True, pady=(0, 12))
        self.preview_text.insert("1.0", "Select a book from the search results to inspect external metadata and import into the local inventory.")
        self.preview_text.config(state="disabled")

        self.import_btn = ttk.Button(
            self.detail_card,
            text="📥 Import to Local Catalog",
            style="Success.TButton",
            state="disabled",
            command=self._open_import_dialog
        )
        self.import_btn.pack(fill="x")

    def _start_search(self) -> None:
        query = self.search_ent.get().strip()
        if not query:
            messagebox.showwarning("Input Required", "Please enter a search term.")
            return

        self.search_btn.config(state="disabled")
        self.status_lbl.config(text="⏳ Querying Google Books API in background...", fg=THEME_COLORS["primary"])

        # Module III: Run I/O-bound REST API call in background thread via BackgroundTaskWorker
        self.task_worker.run_in_thread(
            target_fn=self.api.search_books,
            args=(query,),
            on_success=self._on_search_success,
            on_error=self._on_search_error
        )

    def _on_search_success(self, results: List[Dict[str, Any]]) -> None:
        self.search_btn.config(state="normal")
        self.current_results = results
        self.status_lbl.config(text=f"✓ Found {len(results)} books from Google Books API.", fg=THEME_COLORS["success"])

        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, b in enumerate(results):
            self.tree.insert(
                "", "end",
                iid=str(idx),
                values=(b["title"], b["author"], b["category"], b["publisher"], b["isbn"] or "—")
            )

        if not results:
            self.preview_text.config(state="normal")
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", "No books found matching query. Try another title or keyword.")
            self.preview_text.config(state="disabled")
            self.import_btn.config(state="disabled")

    def _on_search_error(self, exc: Exception) -> None:
        self.search_btn.config(state="normal")
        self.status_lbl.config(text=f"❌ Network/API Error: {exc}", fg=THEME_COLORS["danger"])
        logger.error("API Search failed: %s", exc)
        messagebox.showerror(
            "REST API Error",
            f"Failed to fetch books from Google Books API:\n\n{exc}\n\n"
            "Offline Fallback: The local library catalog and circulation functions remain fully operational."
        )

    def _on_select_item(self, event=None) -> None:
        sel = self.tree.selection()
        if not sel:
            return

        idx = int(sel[0])
        if idx >= len(self.current_results):
            return

        book = self.current_results[idx]
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)

        desc = book.get("description", "No description available.")
        # Truncate long descriptions
        if len(desc) > 500:
            desc = desc[:500] + "..."

        content = (
            f"Title: {book['title']}\n\n"
            f"Author(s): {book['author']}\n"
            f"Category: {book['category']}\n"
            f"Publisher: {book['publisher']} ({book['published_date']})\n"
            f"ISBN: {book['isbn'] or 'N/A'}\n"
            f"Pages: {book['page_count']}\n"
            f"Suggested ID: {book['suggested_book_id']}\n\n"
            f"Synopsis:\n{desc}"
        )
        self.preview_text.insert("1.0", content)
        self.preview_text.config(state="disabled")
        self.import_btn.config(state="normal")

    def _open_import_dialog(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return

        idx = int(sel[0])
        book = self.current_results[idx]

        def on_confirmed(payload):
            try:
                self.book_service.add_book(**payload)
                messagebox.showinfo("Import Successful", f"'{payload['title']}' has been added to your local library catalog!")
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to save to local database: {e}")

        ExternalBookImportDialog(self, book_data=book, on_import_confirmed=on_confirmed)
