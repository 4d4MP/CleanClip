"""Graphical application entry point for CleanClip."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from typing import List, Dict

import ttkbootstrap as ttk

from .config import (
    load_patterns,
    save_patterns,
    serialize_patterns,
    parse_patterns_text,
)
from .sanitizer import apply_sanitization, has_sensitive_data


class PatternEditor(ttk.Toplevel):
    """A simple text editor for managing regex patterns."""

    def __init__(self, master: ttk.Window, patterns: List[Dict[str, str]]):
        super().__init__(master)
        self.title("CleanClip Patterns")
        self.geometry("420x320")
        self.resizable(True, True)
        self.patterns = patterns
        self.transient(master)
        self.grab_set()

        self._create_widgets()
        self._populate_text()

    def _create_widgets(self) -> None:
        instructions = (
            "Edit regex patterns below. Each line must use the format:\n"
            "pattern -> placeholder"
        )
        ttk.Label(self, text=instructions, wraplength=380, anchor="w", justify="left").pack(
            fill=tk.X, padx=12, pady=(12, 6)
        )

        self.text = ScrolledText(self, font=("Courier", 10))
        self.text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

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

    def _populate_text(self) -> None:
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, serialize_patterns(self.patterns))

    def _cancel(self) -> None:
        self.destroy()

    def _save(self) -> None:
        text = self.text.get("1.0", tk.END)
        try:
            patterns = parse_patterns_text(text)
        except ValueError as exc:
            messagebox.showerror("Invalid patterns", str(exc), parent=self)
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
