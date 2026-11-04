"""
ReBuild desktop client (Tkinter).

Run from repo root:
  python desktop/app.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List

from matching import (
    AVAILABILITY_OPTIONS,
    CONDITION_RANK,
    MaterialListing,
    MaterialRequirement,
    find_matches,
    normalise_condition,
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
        self._match_notes: Dict[str, str] = {}
        self._style = apply_theme(self)

        self.listing_count = tk.StringVar(value="0 listings")
        self.status = tk.StringVar(value="Ready — register surplus or search for matches")

        self._build_header()
        self._build_body()
        self._build_status_bar()

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

        self._register_tab(notebook)
        self._search_tab(notebook)
        self._inventory_tab(notebook)

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
        row += 1
        self._form_field(
            card,
            row,
            "Material type",
            ttk.Entry(card, textvariable=fields["material"], width=42),
        )
        row += 1
        self._form_field(
            card,
            row,
            "Available quantity",
            ttk.Entry(card, textvariable=fields["quantity"], width=16),
        )
        row += 1
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
            material = fields["material"].get().strip()
            location = fields["location"].get().strip()
            if not project or not material or not location:
                messagebox.showerror("Invalid input", "Fill in project, material, and location.")
                return

            self.listings.append(
                MaterialListing(
                    project=project,
                    material=material.title(),
                    quantity=qty,
                    condition=cond,
                    location=location,
                    availability=fields["availability"].get(),
                )
            )
            self._refresh_inventory_tree()
            self._update_counts()
            self.status.set(f"Registered {material.title()} successfully")
            messagebox.showinfo("Success", "Material successfully registered!")
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
            "condition": tk.StringVar(value="Good"),
            "location": tk.StringVar(),
        }

        labels = [
            ("Project name", "project", "entry"),
            ("Required material", "material", "entry"),
            ("Required quantity", "quantity", "entry"),
            ("Minimum condition", "condition", "combo"),
            ("Project location", "location", "entry"),
        ]
        for i, (label, key, kind) in enumerate(labels):
            if kind == "combo":
                w = ttk.Combobox(
                    form,
                    textvariable=req[key],
                    values=[c.title() for c in CONDITION_RANK],
                    state="readonly",
                    width=18,
                )
            else:
                w = ttk.Entry(form, textvariable=req[key], width=36)
            self._form_field(form, i, label, w)

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

            if not self.listings:
                messagebox.showinfo("No listings", "Register surplus materials first.")
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

            requirement = MaterialRequirement(
                project=req["project"].get().strip(),
                material=req["material"].get().strip().title(),
                quantity=qty,
                condition=cond,
                location=req["location"].get().strip(),
            )

            matches = find_matches(self.listings, requirement)
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
                        m.supplier.quantity,
                        m.supplier.condition.title(),
                        m.supplier.location,
                        m.compatibility,
                    ),
                    tags=(tag,),
                )
                self._match_notes[iid] = note_text
            self.status.set(f"Found {len(matches)} match(es) — select a row for notes")

        btn_row = ttk.Frame(form, style="Card.TFrame")
        btn_row.grid(row=len(labels), column=0, columnspan=2, sticky=tk.E, pady=(12, 0))
        ttk.Button(btn_row, text="Find matches", style="Primary.TButton", command=run_search).pack(
            side=tk.RIGHT
        )

    def _inventory_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=4)
        notebook.add(tab, text="  All listings  ")

        toolbar = ttk.Frame(tab)
        toolbar.pack(fill=tk.X, pady=(4, 8))
        ttk.Label(toolbar, text="Registered surplus materials in this session", style="Muted.TLabel").pack(
            side=tk.LEFT
        )

        def clear_all() -> None:
            if not self.listings:
                return
            if messagebox.askyesno("Clear all", "Remove every registered listing?"):
                self.listings.clear()
                self._refresh_inventory_tree()
                self._update_counts()
                self.status.set("All listings cleared")

        ttk.Button(toolbar, text="Refresh", style="Secondary.TButton", command=self._refresh_inventory_tree).pack(
            side=tk.RIGHT, padx=(6, 0)
        )
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
        for item in self.listings:
            self.inventory_tree.insert(
                "",
                tk.END,
                values=(
                    item.project,
                    item.material,
                    item.quantity,
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
