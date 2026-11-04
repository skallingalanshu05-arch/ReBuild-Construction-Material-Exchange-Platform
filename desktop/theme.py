"""ReBuild brand colors and ttk styles (aligned with web app tokens)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Tuple

# Brand palette (#173B35, #24594C, #48A879, #F7F9F8)
PRIMARY = "#173B35"
SECONDARY = "#24594C"
LEAF = "#48A879"
LEAF_SOFT = "#E3F2EA"
BG = "#F7F9F8"
CARD = "#FFFFFF"
MUTED = "#5C6B73"
BORDER = "#DDE3E0"
TEXT = "#1F2937"
WARNING_BG = "#FFF8E6"
LOW_BG = "#FDEDED"

FONT_FAMILY = "Segoe UI"
FONT_DISPLAY = ("Segoe UI", 20, "bold")
FONT_TITLE = ("Segoe UI", 11, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_STAT = ("Segoe UI", 11, "bold")


def pick_fonts() -> Tuple[str, Tuple, Tuple, Tuple, Tuple]:
    import sys

    family = "Segoe UI" if sys.platform == "win32" else "Helvetica Neue"
    return (
        family,
        (family, 20, "bold"),
        (family, 11, "bold"),
        (family, 10),
        (family, 9),
    )


def apply_theme(root: tk.Misc) -> ttk.Style:
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    elif "vista" in style.theme_names():
        style.theme_use("vista")

    family, display, title, body, small = pick_fonts()

    root.configure(bg=BG)

    style.configure(".", background=BG, foreground=TEXT, font=body)
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD)
    style.configure("TLabel", background=BG, foreground=TEXT, font=body)
    style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=small)
    style.configure("Card.TLabel", background=CARD, foreground=TEXT, font=body)
    style.configure("CardTitle.TLabel", background=CARD, foreground=PRIMARY, font=title)
    style.configure("Field.TLabel", background=CARD, foreground=TEXT, font=body)

    style.configure(
        "Header.TFrame",
        background=PRIMARY,
    )
    style.configure(
        "HeaderTitle.TLabel",
        background=PRIMARY,
        foreground="#FFFFFF",
        font=display,
    )
    style.configure(
        "HeaderSub.TLabel",
        background=PRIMARY,
        foreground="#CFE8DC",
        font=body,
    )
    style.configure(
        "HeaderBadge.TLabel",
        background=SECONDARY,
        foreground="#FFFFFF",
        font=title,
        padding=(12, 6),
    )

    style.configure(
        "TNotebook",
        background=BG,
        borderwidth=0,
        tabmargins=[2, 6, 2, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background=BG,
        foreground=MUTED,
        padding=[18, 10],
        font=title,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", CARD), ("active", LEAF_SOFT)],
        foreground=[("selected", PRIMARY), ("active", PRIMARY)],
        expand=[("selected", [1, 1, 1, 0])],
    )

    style.configure(
        "TLabelframe",
        background=CARD,
        bordercolor=BORDER,
        relief=tk.GROOVE,
    )
    style.configure(
        "TLabelframe.Label",
        background=CARD,
        foreground=PRIMARY,
        font=title,
    )

    style.configure(
        "Primary.TButton",
        background=LEAF,
        foreground="#FFFFFF",
        font=title,
        padding=(16, 10),
        borderwidth=0,
    )
    style.map(
        "Primary.TButton",
        background=[("active", SECONDARY), ("pressed", PRIMARY)],
    )
    style.configure(
        "Secondary.TButton",
        background=CARD,
        foreground=PRIMARY,
        font=body,
        padding=(12, 8),
        borderwidth=1,
    )
    style.map(
        "Secondary.TButton",
        background=[("active", LEAF_SOFT)],
    )

    style.configure(
        "Status.TLabel",
        background=SECONDARY,
        foreground="#FFFFFF",
        font=small,
        padding=(10, 6),
    )

    style.configure(
        "Treeview",
        background=CARD,
        fieldbackground=CARD,
        foreground=TEXT,
        rowheight=28,
        font=body,
        bordercolor=BORDER,
    )
    style.configure(
        "Treeview.Heading",
        background=LEAF_SOFT,
        foreground=PRIMARY,
        font=title,
        relief=tk.FLAT,
    )
    style.map("Treeview", background=[("selected", LEAF_SOFT)], foreground=[("selected", PRIMARY)])

    style.configure("TEntry", padding=6)
    style.configure("TCombobox", padding=4)

    return style


def score_tag(score: float) -> str:
    if score >= 80:
        return "match_high"
    if score >= 60:
        return "match_mid"
    return "match_low"


def configure_tree_tags(tree: ttk.Treeview) -> None:
    tree.tag_configure("match_high", background=LEAF_SOFT)
    tree.tag_configure("match_mid", background=WARNING_BG)
    tree.tag_configure("match_low", background=LOW_BG)
