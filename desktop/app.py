"""
ReBuild desktop client (Tkinter).

Run from repo root:
  python desktop/app.py

Requires Python 3.11+ with Tk (included on Windows/macOS Python installers).
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import List

from matching import (
    AVAILABILITY_OPTIONS,
    CONDITION_RANK,
    MaterialListing,
    MaterialRequirement,
    find_matches,
    normalise_condition,
)


class ReBuildApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ReBuild — C&D Material Exchange")
        self.geometry("920x620")
        self.minsize(800, 520)

        self.listings: List[MaterialListing] = []

        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")

        header = ttk.Label(
            self,
            text="Construction & Demolition Material Resource Exchange",
            font=("Segoe UI", 14, "bold"),
        )
        header.pack(pady=(12, 4))
        sub = ttk.Label(
            self,
            text="Register surplus materials, search requirements, and view match scores.",
        )
        sub.pack(pady=(0, 8))

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        self._register_tab(notebook)
        self._search_tab(notebook)
        self._inventory_tab(notebook)

        self.status = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W).pack(
            fill=tk.X, padx=12, pady=(0, 8)
        )

    def _register_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text="Register surplus")

        fields = {
            "project": tk.StringVar(),
            "material": tk.StringVar(),
            "quantity": tk.StringVar(),
            "condition": tk.StringVar(value="Good"),
            "location": tk.StringVar(),
            "availability": tk.StringVar(value="Ready"),
        }

        row = 0
        ttk.Label(frame, text="Project name").grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Entry(frame, textvariable=fields["project"], width=40).grid(
            row=row, column=1, sticky=tk.EW, pady=4
        )
        row += 1
        ttk.Label(frame, text="Material type").grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Entry(frame, textvariable=fields["material"], width=40).grid(
            row=row, column=1, sticky=tk.EW, pady=4
        )
        row += 1
        ttk.Label(frame, text="Available quantity").grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Entry(frame, textvariable=fields["quantity"], width=20).grid(
            row=row, column=1, sticky=tk.W, pady=4
        )
        row += 1
        ttk.Label(frame, text="Condition").grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Combobox(
            frame,
            textvariable=fields["condition"],
            values=[c.title() for c in CONDITION_RANK],
            state="readonly",
            width=18,
        ).grid(row=row, column=1, sticky=tk.W, pady=4)
        row += 1
        ttk.Label(frame, text="Location").grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Entry(frame, textvariable=fields["location"], width=40).grid(
            row=row, column=1, sticky=tk.EW, pady=4
        )
        row += 1
        ttk.Label(frame, text="Availability").grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Combobox(
            frame,
            textvariable=fields["availability"],
            values=list(AVAILABILITY_OPTIONS.values()),
            state="readonly",
            width=22,
        ).grid(row=row, column=1, sticky=tk.W, pady=4)
        frame.columnconfigure(1, weight=1)

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

            listing = MaterialListing(
                project=project,
                material=material.title(),
                quantity=qty,
                condition=cond,
                location=location,
                availability=fields["availability"].get(),
            )
            self.listings.append(listing)
            self._refresh_inventory_tree()
            self.status.set(f"Registered {material.title()} — {len(self.listings)} listing(s) total")
            messagebox.showinfo("Success", "Material successfully registered!")
            fields["quantity"].set("")
            fields["material"].set("")

        ttk.Button(frame, text="Save listing", command=submit).grid(
            row=row + 1, column=1, sticky=tk.E, pady=16
        )

    def _search_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text="Search & match")

        req = {
            "project": tk.StringVar(),
            "material": tk.StringVar(),
            "quantity": tk.StringVar(),
            "condition": tk.StringVar(value="Good"),
            "location": tk.StringVar(),
        }

        form = ttk.LabelFrame(frame, text="Your requirement", padding=10)
        form.pack(fill=tk.X)

        labels = [
            ("Project name", "project"),
            ("Required material", "material"),
            ("Required quantity", "quantity"),
            ("Minimum condition", "condition"),
            ("Project location", "location"),
        ]
        for i, (label, key) in enumerate(labels):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky=tk.W, pady=3)
            if key == "condition":
                ttk.Combobox(
                    form,
                    textvariable=req[key],
                    values=[c.title() for c in CONDITION_RANK],
                    state="readonly",
                    width=18,
                ).grid(row=i, column=1, sticky=tk.W, pady=3)
            else:
                ttk.Entry(form, textvariable=req[key], width=36).grid(
                    row=i, column=1, sticky=tk.EW, pady=3
                )
        form.columnconfigure(1, weight=1)

        results_frame = ttk.LabelFrame(frame, text="Matching results", padding=8)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        cols = ("score", "project", "material", "qty", "condition", "location", "fit")
        self.match_tree = ttk.Treeview(results_frame, columns=cols, show="headings", height=12)
        headings = {
            "score": "Score %",
            "project": "Supplier project",
            "material": "Material",
            "qty": "Qty",
            "condition": "Condition",
            "location": "Location",
            "fit": "Compatibility",
        }
        for c in cols:
            self.match_tree.heading(c, text=headings[c])
            self.match_tree.column(c, width=100 if c != "project" else 140)
        scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.match_tree.yview)
        self.match_tree.configure(yscrollcommand=scroll.set)
        self.match_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.match_notes = tk.Text(results_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        self.match_notes.pack(fill=tk.X, pady=(8, 0))

        def on_select(_event=None) -> None:
            sel = self.match_tree.selection()
            if not sel:
                return
            item = self.match_tree.item(sel[0])
            notes = item.get("tags", [""])[0] if item.get("tags") else ""
            self.match_notes.configure(state=tk.NORMAL)
            self.match_notes.delete("1.0", tk.END)
            self.match_notes.insert(tk.END, notes or "No additional notes.")
            self.match_notes.configure(state=tk.DISABLED)

        self.match_tree.bind("<<TreeviewSelect>>", on_select)

        def run_search() -> None:
            for row in self.match_tree.get_children():
                self.match_tree.delete(row)
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
                self.status.set("Search complete — no suppliers found for this material")
                messagebox.showinfo("No matches", "No suppliers found for this material.")
                return

            for m in matches:
                note_text = "; ".join(m.notes) if m.notes else "Meets basic criteria."
                self.match_tree.insert(
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
                    tags=(note_text,),
                )
            self.status.set(f"Found {len(matches)} match(es)")

        ttk.Button(form, text="Find matches", command=run_search).grid(
            row=len(labels), column=1, sticky=tk.E, pady=(8, 0)
        )

    def _inventory_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text="All listings")

        cols = ("project", "material", "quantity", "condition", "location", "availability")
        self.inventory_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.inventory_tree.heading(c, text=c.replace("_", " ").title())
            self.inventory_tree.column(c, width=120)
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scroll.set)
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        btns = ttk.Frame(frame)
        btns.pack(fill=tk.X, pady=(8, 0))

        def clear_all() -> None:
            if not self.listings:
                return
            if messagebox.askyesno("Clear all", "Remove every registered listing?"):
                self.listings.clear()
                self._refresh_inventory_tree()
                self.status.set("All listings cleared")

        ttk.Button(btns, text="Refresh", command=self._refresh_inventory_tree).pack(
            side=tk.LEFT
        )
        ttk.Button(btns, text="Clear all", command=clear_all).pack(side=tk.LEFT, padx=8)

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


def main() -> None:
    app = ReBuildApp()
    app.mainloop()


if __name__ == "__main__":
    main()
