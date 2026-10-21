"""Member Management View with search, registration, and safe deletion."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from services.member_service import MemberService
from models.member import Member
from config import THEME_COLORS
from gui.styles import UIStyleHelper
from utils.logging_config import get_logger

logger = get_logger("gui.members_view")


class MemberFormDialog(tk.Toplevel):
    """Modal dialog for registering or modifying a library member."""

    def __init__(self, parent: tk.Widget, title: str, member: Optional[Member] = None, on_save: Optional[Callable[[dict], None]] = None):
        super().__init__(parent)
        self.title(title)
        self.geometry("440x380")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.member = member
        self.on_save = on_save
        self.configure(bg=THEME_COLORS["card_bg"])

        self._build_form()
        if member:
            self._populate(member)

    def _build_form(self) -> None:
        pad_x = 24
        self.columnconfigure(1, weight=1)

        header = tk.Label(
            self,
            text="Register Member" if not self.member else f"Edit Member: {self.member.member_id}",
            font=UIStyleHelper.FONT_HEADER,
            bg=THEME_COLORS["card_bg"],
            fg=THEME_COLORS["primary"]
        )
        header.grid(row=0, column=0, columnspan=2, padx=pad_x, pady=(20, 16), sticky="w")

        fields = [
            ("Member ID:", "id_ent"),
            ("Full Name:", "name_ent"),
            ("Email Address:", "email_ent"),
            ("Phone Number:", "phone_ent"),
        ]

        self.entries = {}
        for idx, (label_text, attr) in enumerate(fields, start=1):
            lbl = tk.Label(self, text=label_text, font=UIStyleHelper.FONT_SUBHEADER, bg=THEME_COLORS["card_bg"], fg=THEME_COLORS["text_dark"])
            lbl.grid(row=idx, column=0, padx=pad_x, pady=8, sticky="w")

            ent = ttk.Entry(self, font=UIStyleHelper.FONT_BODY)
            ent.grid(row=idx, column=1, padx=pad_x, pady=8, sticky="ew")
            self.entries[attr] = ent

        if self.member:
            self.entries["id_ent"].config(state="disabled")

        btn_frame = tk.Frame(self, bg=THEME_COLORS["card_bg"])
        btn_frame.grid(row=len(fields) + 1, column=0, columnspan=2, padx=pad_x, pady=24, sticky="e")

        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="right", padx=(8, 0))

        save_btn = ttk.Button(btn_frame, text="Save Member", style="Success.TButton", command=self._submit)
        save_btn.pack(side="right")

    def _populate(self, member: Member) -> None:
        self.entries["id_ent"].insert(0, member.member_id)
        self.entries["name_ent"].insert(0, member.name)
        self.entries["email_ent"].insert(0, member.email)
        self.entries["phone_ent"].insert(0, member.phone)

    def _submit(self) -> None:
        m_id = self.member.member_id if self.member else self.entries["id_ent"].get().strip()
        name = self.entries["name_ent"].get().strip()
        email = self.entries["email_ent"].get().strip()
        phone = self.entries["phone_ent"].get().strip()

        data = {
            "member_id": m_id,
            "name": name,
            "email": email,
            "phone": phone
        }
        if self.on_save:
            self.on_save(data)
        self.destroy()


class MembersView(ttk.Frame):
    """View managing registered members."""

    def __init__(self, parent: tk.Widget, member_service: MemberService, on_data_changed: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.member_service = member_service
        self.on_data_changed = on_data_changed

        self.configure(style="TFrame")
        self._build_ui()
        self.load_members()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        hdr = tk.Frame(self, bg=THEME_COLORS["content_bg"])
        hdr.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        title = tk.Label(hdr, text="Member Registry & Borrowers", font=UIStyleHelper.FONT_TITLE, bg=THEME_COLORS["content_bg"], fg=THEME_COLORS["text_dark"])
        title.pack(side="left")

        act_frame = tk.Frame(hdr, bg=THEME_COLORS["content_bg"])
        act_frame.pack(side="right")

        ttk.Button(act_frame, text="➕ Register Member", style="Success.TButton", command=self._open_register_dialog).pack(side="left", padx=4)
        ttk.Button(act_frame, text="✏️ Edit", command=self._open_edit_dialog).pack(side="left", padx=4)
        ttk.Button(act_frame, text="🗑️ Delete", style="Danger.TButton", command=self._delete_member).pack(side="left", padx=4)
        ttk.Button(act_frame, text="📤 Export", command=self._export_members).pack(side="left", padx=4)

        # Search Bar
        search_bar = tk.Frame(self, bg=THEME_COLORS["card_bg"], padx=16, pady=10, relief="solid", bd=1)
        search_bar.grid(row=1, column=0, sticky="ew", padx=24, pady=8)

        tk.Label(search_bar, text="Search Members:", font=UIStyleHelper.FONT_SUBHEADER, bg=THEME_COLORS["card_bg"]).pack(side="left", padx=(0, 8))
        self.search_ent = ttk.Entry(search_bar, width=32)
        self.search_ent.pack(side="left", padx=(0, 10))
        self.search_ent.bind("<Return>", lambda e: self.load_members())

        ttk.Button(search_bar, text="🔍 Search", command=self.load_members).pack(side="left", padx=4)
        ttk.Button(search_bar, text="Reset", command=self._reset_search).pack(side="left", padx=4)

        # Table Frame
        table_frame = tk.Frame(self, bg=THEME_COLORS["card_bg"], bd=1, relief="solid")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=24, pady=(8, 20))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("id", "name", "email", "phone", "created_at")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="Member ID")
        self.tree.heading("name", text="Full Name")
        self.tree.heading("email", text="Email Address")
        self.tree.heading("phone", text="Phone Number")
        self.tree.heading("created_at", text="Registered On")

        self.tree.column("id", width=110, anchor="center")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("email", width=240, anchor="w")
        self.tree.column("phone", width=150, anchor="center")
        self.tree.column("created_at", width=180, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<Double-1>", lambda e: self._open_edit_dialog())

    def load_members(self) -> None:
        query = self.search_ent.get().strip()
        members = self.member_service.search_members(query) if query else self.member_service.get_all_members()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for m in members:
            self.tree.insert(
                "",
                "end",
                iid=m.member_id,
                values=(m.member_id, m.name, m.email, m.phone, m.created_at[:19].replace("T", " "))
            )

    def _reset_search(self) -> None:
        self.search_ent.delete(0, tk.END)
        self.load_members()

    def _open_register_dialog(self) -> None:
        def on_save(data):
            try:
                self.member_service.register_member(**data)
                self.load_members()
                if self.on_data_changed:
                    self.on_data_changed()
                messagebox.showinfo("Success", f"Member '{data['name']}' registered successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        MemberFormDialog(self, title="Register New Member", member=None, on_save=on_save)

    def _open_edit_dialog(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a member to edit.")
            return

        m_id = sel[0]
        member = self.member_service.get_member(m_id)
        if not member:
            messagebox.showerror("Error", "Member not found.")
            return

        def on_save(data):
            try:
                self.member_service.update_member(**data)
                self.load_members()
                if self.on_data_changed:
                    self.on_data_changed()
                messagebox.showinfo("Success", f"Member '{data['member_id']}' updated.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        MemberFormDialog(self, title="Edit Member", member=member, on_save=on_save)

    def _delete_member(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a member to delete.")
            return

        m_id = sel[0]
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete member '{m_id}'?\n\nThis cannot be undone."
        )
        if not confirm:
            return

        try:
            self.member_service.delete_member(m_id)
            self.load_members()
            if self.on_data_changed:
                self.on_data_changed()
            messagebox.showinfo("Success", f"Member '{m_id}' deleted.")
        except Exception as e:
            messagebox.showerror("Cannot Delete", str(e))

    def _export_members(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Export Members",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("JSON Files", "*.json")]
        )
        if not file_path:
            return

        fmt = "JSON" if file_path.endswith(".json") else "CSV"
        try:
            self.member_service.export_members(file_path, fmt)
            messagebox.showinfo("Export Success", f"Members exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
