"""Graphical application entry point for CleanClip."""

from __future__ import annotations

import re
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Tuple

import ttkbootstrap as ttk

from .config import load_patterns, save_patterns
from .sanitizer import apply_sanitization, has_sensitive_data


class PatternEditor(ttk.Toplevel):
    """A simple text editor for managing regex patterns."""

    def __init__(self, master: ttk.Window, patterns: List[Dict[str, str]]):
        super().__init__(master)
        self.title("CleanClip Patterns")
        self.geometry("520x420")
        self.resizable(True, True)
        self.patterns = patterns
        self._rows: List[Tuple[tk.StringVar, tk.StringVar, ttk.Frame]] = []
        self.transient(master)
        self.grab_set()

        self._create_widgets()
        self._populate_rows()

    def _create_widgets(self) -> None:
        instructions = (
            "Modify the regular expressions and placeholders below."
            " Each row maps a regex to the placeholder text that will replace matches."
        )
        ttk.Label(self, text=instructions, wraplength=460, anchor="w", justify="left").pack(
            fill=tk.X, padx=16, pady=(16, 8)
        )

        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=16)

        header = ttk.Frame(container)
        header.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(header, text="Pattern", width=28, anchor="w").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(header, text="Placeholder", width=22, anchor="w").pack(side=tk.LEFT)

        self.pattern_frame = ttk.Frame(container)
        self.pattern_frame.pack(fill=tk.BOTH, expand=True)

        add_btn = ttk.Button(
            container,
            text="+ Add Pattern",
            bootstyle="info-outline",
            command=lambda: self._add_pattern_row("", ""),
        )
        add_btn.pack(anchor=tk.W, pady=(8, 12))

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=16, pady=(0, 16))

        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel,
            bootstyle="secondary-outline",
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(0, 8))

        save_btn = ttk.Button(
            button_frame,
            text="Save",
            bootstyle="success",
            command=self._save,
        )
        save_btn.pack(side=tk.RIGHT)

    def _populate_rows(self) -> None:
        if not self.patterns:
            self._add_pattern_row("", "")
            return
        for entry in self.patterns:
            self._add_pattern_row(entry.get("pattern", ""), entry.get("placeholder", ""))

    def _add_pattern_row(self, pattern: str, placeholder: str) -> None:
        row_frame = ttk.Frame(self.pattern_frame)
        row_frame.pack(fill=tk.X, pady=4)

        pattern_var = tk.StringVar(value=pattern)
        placeholder_var = tk.StringVar(value=placeholder)

        pattern_entry = ttk.Entry(row_frame, textvariable=pattern_var, width=32)
        pattern_entry.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)

        placeholder_entry = ttk.Entry(row_frame, textvariable=placeholder_var, width=26)
        placeholder_entry.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)

        remove_btn = ttk.Button(
            row_frame,
            text="✕",
            width=3,
            bootstyle="danger-outline",
            command=lambda: self._remove_row(row_frame),
        )
        remove_btn.pack(side=tk.LEFT)

        self._rows.append((pattern_var, placeholder_var, row_frame))

    def _remove_row(self, row_frame: ttk.Frame) -> None:
        for idx, (_, _, frame) in enumerate(self._rows):
            if frame is row_frame:
                frame.destroy()
                del self._rows[idx]
                break
        if not self._rows:
            self._add_pattern_row("", "")

    def _cancel(self) -> None:
        self.destroy()

    def _save(self) -> None:
        patterns: List[Dict[str, str]] = []
        for pattern_var, placeholder_var, _ in self._rows:
            pattern = pattern_var.get().strip()
            placeholder = placeholder_var.get().strip()
            if not pattern and not placeholder:
                continue
            if not pattern or not placeholder:
                messagebox.showerror(
                    "Invalid pattern",
                    "Each row must include both a regex pattern and a placeholder.",
                    parent=self,
                )
                return
            try:
                re.compile(pattern)
            except re.error as exc:
                messagebox.showerror(
                    "Invalid regex",
                    f"Pattern '{pattern}' is not a valid regular expression: {exc}",
                    parent=self,
                )
                return
            patterns.append({"pattern": pattern, "placeholder": placeholder})

        if not patterns:
            messagebox.showerror(
                "No patterns provided", "Add at least one pattern before saving.", parent=self
            )
            return

        save_patterns(patterns)
        self.patterns = patterns
        messagebox.showinfo("Patterns saved", "New patterns stored successfully.", parent=self)
        self.destroy()


def run() -> None:
    """Launch the CleanClip application."""

    load_patterns()  # Ensure configuration exists before building the UI.

    app = ttk.Window(title="CleanClip", themename="cyborg")
    app.geometry("300x180")
    app.resizable(False, False)

    main_frame = ttk.Frame(app, padding=12)
    main_frame.pack(fill=tk.BOTH, expand=True)

    gear_button = ttk.Button(
        main_frame,
        text="⚙",
        command=lambda: PatternEditor(app, load_patterns()),
        width=3,
        bootstyle="secondary-link",
        style="Gear.TButton",
    )
    gear_button.pack(anchor=tk.NE)

    style = ttk.Style()
    style.configure("Gear.TButton", font=("Segoe UI Symbol", 16))
    style.configure(
        "Clean.TButton",
        font=("Helvetica", 12, "bold"),
        padding=(18, 14),
    )

    def on_click() -> None:
        try:
            original = app.clipboard_get()
        except tk.TclError:
            messagebox.showwarning(
                "Clipboard empty", "No text data was found on the clipboard.", parent=app
            )
            return

        current_patterns = load_patterns()
        sanitized = apply_sanitization(original, current_patterns)
        app.clipboard_clear()
        app.clipboard_append(sanitized)

        if has_sensitive_data(original, sanitized):
            messagebox.showinfo(
                "Clipboard sanitized",
                "Sensitive data was replaced with placeholders.",
                parent=app,
            )
        else:
            messagebox.showinfo(
                "Clipboard unchanged",
                "No sensitive data was detected.",
                parent=app,
            )

    sanitize_button = ttk.Button(
        main_frame,
        text="Sanitize Clipboard Contents",
        command=on_click,
        bootstyle="success-outline",
        style="Clean.TButton",
        width=22,
    )
    sanitize_button.pack(pady=(20, 12))

    app.mainloop()


if __name__ == "__main__":  # pragma: no cover
    run()
