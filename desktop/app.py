"""
ReBuild desktop client (Tkinter).

Run from repo root:
  python desktop/app.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List, Optional

from api_client import ApiError, ReBuildApiClient
from backend_map import (
    build_material_create_payload,
    category_id_for_material,
    doc_to_listing,
    listing_matches_type,
)
from config import load_config, load_session, save_config, save_session
from matching import (
    AVAILABILITY_OPTIONS,
    CONDITION_RANK,
    MaterialListing,
    MaterialRequirement,
    find_matches,
    normalise_condition,
)
from material_types import (
    MATERIAL_TYPE_NAMES,
    format_unit,
    get_spec,
    quantity_field_label,
    resolve_unit,
)
from theme import (
    BG,
    CARD,
    LEAF,
    PRIMARY,
    apply_theme,
    configure_tree_tags,
    score_tag,
)


class ReBuildApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ReBuild — Material Exchange")
        self.geometry("980x680")
        self.minsize(860, 580)
        self.configure(bg=BG)

        self.listings: List[MaterialListing] = []
        self._categories: List[dict] = []
        self._match_notes: Dict[str, str] = {}
        self._style = apply_theme(self)
        self._user_email = tk.StringVar(value="Not signed in")
        self._api_url = tk.StringVar(value=load_config().get("api_base_url", "http://127.0.0.1:8000/api/v1"))

        self.api: Optional[ReBuildApiClient] = None

        self.listing_count = tk.StringVar(value="0 listings")
        self.status = tk.StringVar(value="Sign in on the Account tab — data is saved to MongoDB via the API")

        self._build_header()
        self._build_body()
        self._build_status_bar()
        self._init_api_client()

    def _build_header(self) -> None:
        bar = ttk.Frame(self, style="Header.TFrame", padding=(20, 18))
        bar.pack(fill=tk.X)

        left = ttk.Frame(bar, style="Header.TFrame")
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)

        display = self._style.lookup("HeaderTitle.TLabel", "font")
        title_row = tk.Frame(left, bg=PRIMARY)
        title_row.pack(anchor=tk.W)
        tk.Label(title_row, text="Re", bg=PRIMARY, fg="#FFFFFF", font=display).pack(side=tk.LEFT)
        tk.Label(title_row, text="Build", bg=PRIMARY, fg=LEAF, font=display).pack(side=tk.LEFT)

        ttk.Label(
            left,
            text="Construction & demolition material reuse · register · match · exchange",
            style="HeaderSub.TLabel",
        ).pack(anchor=tk.W, pady=(6, 0))

        badge = ttk.Label(bar, textvariable=self.listing_count, style="HeaderBadge.TLabel")
        badge.pack(side=tk.RIGHT, padx=(12, 0))

    def _build_body(self) -> None:
        shell = ttk.Frame(self, padding=(16, 12))
        shell.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(shell)
        notebook.pack(fill=tk.BOTH, expand=True)

        self._account_tab(notebook)
        self._register_tab(notebook)
        self._search_tab(notebook)
        self._inventory_tab(notebook)

    def _init_api_client(self) -> None:
        self.api = ReBuildApiClient(self._api_url.get().strip())
        session = load_session()
        if session:
            self.api.load_tokens(session.get("access_token"), session.get("refresh_token"))
            if session.get("email"):
                self._user_email.set(session["email"])
            try:
                self.api.me()
                self._categories = self.api.list_categories()
                self._refresh_inventory_tree()
                self.status.set("Signed in — listings load from MongoDB")
            except ApiError:
                save_session(None)
                self.api.load_tokens(None, None)
                self._user_email.set("Not signed in")

    def _is_logged_in(self) -> bool:
        return bool(self.api and self.api.access_token)

    def _require_login(self) -> bool:
        if self._is_logged_in():
            return True
        messagebox.showwarning(
            "Sign in required",
            "Open the Account tab, sign in, and ensure the backend is running.\n"
            "Listings are stored in MongoDB through the API.",
        )
        return False

    def _account_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=4)
        notebook.add(tab, text="  Account  ")

        card = self._card(tab, "Backend connection")
        card.pack(fill=tk.X, pady=(4, 10))

        self._form_field(card, 0, "API base URL", ttk.Entry(card, textvariable=self._api_url, width=48))
        ttk.Label(
            card,
            text="Default: http://127.0.0.1:8000/api/v1 — start backend with python run.py and MongoDB running.",
            style="Muted.TLabel",
        ).grid(row=1, column=1, sticky=tk.W)

        cred = self._card(tab, "Sign in")
        cred.pack(fill=tk.X, pady=(0, 10))

        email_var = tk.StringVar()
        password_var = tk.StringVar()
        self._form_field(cred, 0, "Email", ttk.Entry(cred, textvariable=email_var, width=36))
        self._form_field(cred, 1, "Password", ttk.Entry(cred, textvariable=password_var, width=36, show="•"))

        status_card = self._card(tab, "Session")
        status_card.pack(fill=tk.X)
        ttk.Label(status_card, text="Signed in as:", style="Field.TLabel").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(status_card, textvariable=self._user_email, style="Field.TLabel").grid(
            row=0, column=1, sticky=tk.W
        )

        def do_login() -> None:
            url = self._api_url.get().strip()
            if not url:
                messagebox.showerror("Invalid URL", "Enter the API base URL.")
                return
            save_config({"api_base_url": url})
            self.api = ReBuildApiClient(url)
            try:
                self.config(cursor="watch")
                self.api.login(email_var.get().strip(), password_var.get())
                self.api.me()
                self._categories = self.api.list_categories()
            except ApiError as exc:
                messagebox.showerror("Login failed", str(exc))
                return
            finally:
                self.config(cursor="")
            save_session(
                {
                    "access_token": self.api.access_token,
                    "refresh_token": self.api.refresh_token,
                    "email": email_var.get().strip(),
                }
            )
            self._user_email.set(email_var.get().strip())
            password_var.set("")
            self._refresh_inventory_tree()
            self.status.set("Signed in — new listings save to MongoDB")
            messagebox.showinfo("Signed in", "Connected to the backend. Data will persist in MongoDB.")

        def do_logout() -> None:
            if self.api:
                self.api.logout()
            save_session(None)
            self._user_email.set("Not signed in")
            self.listings.clear()
            self._refresh_inventory_tree()
            self.status.set("Signed out")

        btn_row = ttk.Frame(cred, style="Card.TFrame")
        btn_row.grid(row=2, column=1, sticky=tk.E, pady=(12, 0))
        ttk.Button(btn_row, text="Sign in", style="Primary.TButton", command=do_login).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        ttk.Button(btn_row, text="Sign out", style="Secondary.TButton", command=do_logout).pack(
            side=tk.RIGHT
        )

    def _build_status_bar(self) -> None:
        ttk.Label(self, textvariable=self.status, style="Status.TLabel").pack(
            fill=tk.X, side=tk.BOTTOM
        )

    def _card(self, parent: ttk.Frame, title: str) -> ttk.LabelFrame:
        return ttk.LabelFrame(parent, text=f"  {title}  ", padding=16)

    def _form_field(
        self,
        parent: ttk.LabelFrame,
        row: int,
        label: str,
        widget: tk.Widget,
    ) -> None:
        ttk.Label(parent, text=label, style="Field.TLabel").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 12), pady=6
        )
        widget.grid(row=row, column=1, sticky=tk.EW, pady=6)
        parent.columnconfigure(1, weight=1)

    def _material_quantity_block(
        self,
        parent: ttk.LabelFrame,
        row: int,
        fields: Dict[str, tk.StringVar],
        *,
        quantity_label: str = "Quantity",
    ) -> int:
        """Material type dropdown + quantity entry with auto unit from catalogue."""
        fields.setdefault("unit", tk.StringVar(value=""))
        fields.setdefault("steel_unit", tk.StringVar(value="ton"))
        fields.setdefault("quantity_hint", tk.StringVar(value="Select a material type to set the unit."))
        fields.setdefault("quantity_label", tk.StringVar(value=quantity_label))

        material_cb = ttk.Combobox(
            parent,
            textvariable=fields["material"],
            values=MATERIAL_TYPE_NAMES,
            state="readonly",
            width=38,
        )
        self._form_field(parent, row, "Material type", material_cb)
        row += 1

        ttk.Label(parent, textvariable=fields["quantity_label"], style="Field.TLabel").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 12), pady=6
        )
        qty_row = ttk.Frame(parent, style="Card.TFrame")
        qty_row.grid(row=row, column=1, sticky=tk.EW, pady=6)

        ttk.Entry(qty_row, textvariable=fields["quantity"], width=14).pack(side=tk.LEFT)
        unit_lbl = ttk.Label(qty_row, text="", style="Field.TLabel", width=18)
        unit_lbl.pack(side=tk.LEFT, padx=(10, 0))
        steel_cb = ttk.Combobox(
            qty_row,
            textvariable=fields["steel_unit"],
            values=["ton", "kg"],
            state="readonly",
            width=6,
        )

        hint = ttk.Label(parent, textvariable=fields["quantity_hint"], style="Muted.TLabel")
        hint.grid(row=row + 1, column=1, sticky=tk.W, pady=(0, 4))

        def refresh(*_args: object) -> None:
            spec = get_spec(fields["material"].get())
            if not spec:
                unit_lbl.config(text="")
                steel_cb.pack_forget()
                fields["quantity_label"].set(quantity_label)
                fields["quantity_hint"].set("Select a material type to set the unit.")
                return

            fields["quantity_hint"].set(spec.quantity_hint)
            if spec.allows_unit_choice:
                steel_cb.pack(side=tk.LEFT, padx=(8, 0))
                unit = resolve_unit(spec.key, fields["steel_unit"].get())
                fields["unit"].set(unit)
            else:
                steel_cb.pack_forget()
                unit = spec.default_unit
                fields["unit"].set(unit)

            unit_lbl.config(text=format_unit(unit))
            fields["quantity_label"].set(quantity_field_label(spec.key, unit))

        def on_steel_unit(_event=None) -> None:
            fields["unit"].set(fields["steel_unit"].get())
            refresh()

        material_cb.bind("<<ComboboxSelected>>", refresh)
        steel_cb.bind("<<ComboboxSelected>>", on_steel_unit)

        return row + 2

    def _update_counts(self) -> None:
        n = len(self.listings)
        self.listing_count.set(f"{n} listing{'s' if n != 1 else ''}")

    def _register_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=4)
        notebook.add(tab, text="  Register surplus  ")

        hint = ttk.Label(
            tab,
            text="List leftover or reclaimed materials from your site so other projects can find them.",
            style="Muted.TLabel",
        )
        hint.pack(anchor=tk.W, pady=(4, 10))

        card = self._card(tab, "Surplus material details")
        card.pack(fill=tk.BOTH, expand=True)

        fields: Dict[str, tk.StringVar] = {
            "project": tk.StringVar(),
            "material": tk.StringVar(),
            "quantity": tk.StringVar(),
            "condition": tk.StringVar(value="Good"),
            "location": tk.StringVar(),
            "availability": tk.StringVar(value="Ready"),
        }

        row = 0
        self._form_field(card, row, "Project name", ttk.Entry(card, textvariable=fields["project"], width=42))
        row = 1
        row = self._material_quantity_block(
            card,
            row,
            fields,
            quantity_label="Available quantity",
        )
        self._form_field(
            card,
            row,
            "Condition",
            ttk.Combobox(
                card,
                textvariable=fields["condition"],
                values=[c.title() for c in CONDITION_RANK],
                state="readonly",
                width=18,
            ),
        )
        row += 1
        self._form_field(card, row, "Location", ttk.Entry(card, textvariable=fields["location"], width=42))
        row += 1
        self._form_field(
            card,
            row,
            "Availability",
            ttk.Combobox(
                card,
                textvariable=fields["availability"],
                values=list(AVAILABILITY_OPTIONS.values()),
                state="readonly",
                width=22,
            ),
        )

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=row + 1, column=0, columnspan=2, sticky=tk.E, pady=(16, 0))

        def submit() -> None:
            if not self._require_login():
                return
            try:
                qty = float(fields["quantity"].get().strip())
                if qty <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid input", "Enter a positive quantity.")
                return

            cond = normalise_condition(fields["condition"].get())
            if cond not in CONDITION_RANK:
                messagebox.showerror("Invalid input", "Choose a valid condition.")
                return

            project = fields["project"].get().strip()
            location = fields["location"].get().strip()
            spec = get_spec(fields["material"].get())
            if not project or not location or not spec:
                messagebox.showerror(
                    "Invalid input",
                    "Fill in project, location, and choose a material type from the list.",
                )
                return

            unit = resolve_unit(spec.key, fields["unit"].get() or fields["steel_unit"].get())
            if not self._categories:
                try:
                    self._categories = self.api.list_categories()  # type: ignore[union-attr]
                except ApiError as exc:
                    messagebox.showerror("API error", str(exc))
                    return
            cat_id = category_id_for_material(self._categories, spec)
            if not cat_id:
                messagebox.showerror(
                    "Categories missing",
                    f"Category “{spec.category_name}” not found in MongoDB.\n"
                    "Start the backend once to seed categories, then try again.",
                )
                return

            payload = build_material_create_payload(
                spec=spec,
                category_id=cat_id,
                project_name=project,
                quantity=qty,
                unit=unit,
                condition=cond,
                location=location,
                availability=fields["availability"].get(),
            )
            try:
                self.config(cursor="watch")
                assert self.api is not None
                self.api.create_material(payload)
            except ApiError as exc:
                messagebox.showerror("Could not save listing", str(exc))
                return
            finally:
                self.config(cursor="")

            self._refresh_inventory_tree()
            self.status.set(f"Saved {spec.key} ({qty} {format_unit(unit)}) to MongoDB")
            messagebox.showinfo("Success", "Material saved to the database.")
            fields["quantity"].set("")
            fields["material"].set("")

        ttk.Button(actions, text="Save listing", style="Primary.TButton", command=submit).pack(
            side=tk.RIGHT
        )

    def _search_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=4)
        notebook.add(tab, text="  Search & match  ")

        form = self._card(tab, "Your requirement")
        form.pack(fill=tk.X, pady=(4, 10))

        req: Dict[str, tk.StringVar] = {
            "project": tk.StringVar(),
            "material": tk.StringVar(),
            "quantity": tk.StringVar(),
            "unit": tk.StringVar(),
            "steel_unit": tk.StringVar(value="ton"),
            "quantity_hint": tk.StringVar(value="Select a material type to set the unit."),
            "quantity_label": tk.StringVar(value="Required quantity"),
            "condition": tk.StringVar(value="Good"),
            "location": tk.StringVar(),
        }

        srow = 0
        self._form_field(form, srow, "Project name", ttk.Entry(form, textvariable=req["project"], width=36))
        srow += 1
        srow = self._material_quantity_block(form, srow, req, quantity_label="Required quantity")
        self._form_field(
            form,
            srow,
            "Minimum condition",
            ttk.Combobox(
                form,
                textvariable=req["condition"],
                values=[c.title() for c in CONDITION_RANK],
                state="readonly",
                width=18,
            ),
        )
        srow += 1
        self._form_field(form, srow, "Project location", ttk.Entry(form, textvariable=req["location"], width=36))
        form_last_row = srow

        results = self._card(tab, "Matching results")
        results.pack(fill=tk.BOTH, expand=True)

        tree_wrap = ttk.Frame(results, style="Card.TFrame")
        tree_wrap.pack(fill=tk.BOTH, expand=True)

        cols = ("score", "project", "material", "qty", "condition", "location", "fit")
        self.match_tree = ttk.Treeview(tree_wrap, columns=cols, show="headings", height=10)
        headings = {
            "score": "Score %",
            "project": "Supplier project",
            "material": "Material",
            "qty": "Qty",
            "condition": "Condition",
            "location": "Location",
            "fit": "Fit",
        }
        widths = {"score": 72, "project": 150, "material": 120, "qty": 64, "condition": 88, "location": 120, "fit": 120}
        for c in cols:
            self.match_tree.heading(c, text=headings[c])
            self.match_tree.column(c, width=widths.get(c, 100), anchor=tk.W if c != "score" else tk.CENTER)
        configure_tree_tags(self.match_tree)

        scroll = ttk.Scrollbar(tree_wrap, orient=tk.VERTICAL, command=self.match_tree.yview)
        self.match_tree.configure(yscrollcommand=scroll.set)
        self.match_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        notes_lbl = ttk.Label(results, text="Notes for selected match", style="CardTitle.TLabel")
        notes_lbl.pack(anchor=tk.W, pady=(10, 4))
        self.match_notes = tk.Text(
            results,
            height=3,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=CARD,
            fg="#1F2937",
            relief=tk.FLAT,
            padx=8,
            pady=6,
            highlightthickness=1,
            highlightbackground="#DDE3E0",
        )
        self.match_notes.pack(fill=tk.X)

        def on_select(_event=None) -> None:
            sel = self.match_tree.selection()
            if not sel:
                return
            item = self.match_tree.item(sel[0])
            notes = self._match_notes.get(sel[0], "No additional notes.")
            self.match_notes.configure(state=tk.NORMAL)
            self.match_notes.delete("1.0", tk.END)
            self.match_notes.insert(tk.END, notes)
            self.match_notes.configure(state=tk.DISABLED)

        self.match_tree.bind("<<TreeviewSelect>>", on_select)

        def run_search() -> None:
            for row in self.match_tree.get_children():
                self.match_tree.delete(row)
            self._match_notes.clear()
            self.match_notes.configure(state=tk.NORMAL)
            self.match_notes.delete("1.0", tk.END)
            self.match_notes.configure(state=tk.DISABLED)

            if not self.api:
                messagebox.showinfo("No API", "Set the API URL on the Account tab and ensure the backend is running.")
                return

            try:
                qty = float(req["quantity"].get().strip())
                if qty <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid input", "Enter a positive required quantity.")
                return

            cond = normalise_condition(req["condition"].get())
            if cond not in CONDITION_RANK:
                messagebox.showerror("Invalid input", "Choose a valid condition.")
                return

            spec = get_spec(req["material"].get())
            if not spec:
                messagebox.showerror("Invalid input", "Choose a material type from the list.")
                return

            material = spec.key
            unit = resolve_unit(material, req["unit"].get() or req["steel_unit"].get())

            requirement = MaterialRequirement(
                project=req["project"].get().strip(),
                material=material,
                quantity=qty,
                unit=unit,
                condition=cond,
                location=req["location"].get().strip(),
            )

            try:
                self.config(cursor="watch")
                assert self.api is not None
                docs = self.api.search_materials(page_size=100)
            except ApiError as exc:
                messagebox.showerror("API error", str(exc))
                return
            finally:
                self.config(cursor="")

            pool = [doc_to_listing(d) for d in docs if listing_matches_type(d, material)]
            matches = find_matches(pool, requirement)
            if not matches:
                self.status.set("No suppliers found for this material")
                messagebox.showinfo("No matches", "No suppliers found for this material.")
                return

            for m in matches:
                note_text = "; ".join(m.notes) if m.notes else "Meets basic criteria."
                tag = score_tag(m.score)
                iid = self.match_tree.insert(
                    "",
                    tk.END,
                    values=(
                        m.score,
                        m.supplier.project,
                        m.supplier.material,
                        f"{m.supplier.quantity} {format_unit(m.supplier.unit)}",
                        m.supplier.condition.title(),
                        m.supplier.location,
                        m.compatibility,
                    ),
                    tags=(tag,),
                )
                self._match_notes[iid] = note_text
            self.status.set(f"Found {len(matches)} match(es) — select a row for notes")

        btn_row = ttk.Frame(form, style="Card.TFrame")
        btn_row.grid(row=form_last_row + 1, column=0, columnspan=2, sticky=tk.E, pady=(12, 0))
        ttk.Button(btn_row, text="Find matches", style="Primary.TButton", command=run_search).pack(
            side=tk.RIGHT
        )

    def _inventory_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=4)
        notebook.add(tab, text="  All listings  ")

        toolbar = ttk.Frame(tab)
        toolbar.pack(fill=tk.X, pady=(4, 8))
        ttk.Label(
            toolbar,
            text="Your company's listings stored in MongoDB (refresh after saving)",
            style="Muted.TLabel",
        ).pack(side=tk.LEFT)

        def clear_all() -> None:
            messagebox.showinfo(
                "Not available",
                "Listings live in MongoDB. Use the web app or API to deactivate listings.",
            )

        ttk.Button(
            toolbar,
            text="Refresh from database",
            style="Secondary.TButton",
            command=self._refresh_inventory_tree,
        ).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(toolbar, text="Clear all", style="Secondary.TButton", command=clear_all).pack(
            side=tk.RIGHT
        )

        card = self._card(tab, "Inventory")
        card.pack(fill=tk.BOTH, expand=True)

        tree_wrap = ttk.Frame(card, style="Card.TFrame")
        tree_wrap.pack(fill=tk.BOTH, expand=True)

        cols = ("project", "material", "quantity", "condition", "location", "availability")
        self.inventory_tree = ttk.Treeview(tree_wrap, columns=cols, show="headings", height=14)
        for c in cols:
            self.inventory_tree.heading(c, text=c.replace("_", " ").title())
            self.inventory_tree.column(c, width=130, anchor=tk.W)
        scroll = ttk.Scrollbar(tree_wrap, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scroll.set)
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _refresh_inventory_tree(self) -> None:
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)

        if not self._is_logged_in() or not self.api:
            self.listings = []
            self._update_counts()
            return

        try:
            self.config(cursor="watch")
            docs = self.api.my_listings()
        except ApiError as exc:
            messagebox.showerror("Could not load listings", str(exc))
            return
        finally:
            self.config(cursor="")

        self.listings = [doc_to_listing(d) for d in docs]
        for item in self.listings:
            self.inventory_tree.insert(
                "",
                tk.END,
                values=(
                    item.project,
                    item.material,
                    f"{item.quantity} {format_unit(item.unit)}",
                    item.condition.title(),
                    item.location,
                    item.availability,
                ),
            )
        self._update_counts()


def main() -> None:
    app = ReBuildApp()
    app.mainloop()


if __name__ == "__main__":
    main()
