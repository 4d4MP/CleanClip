"""CleanClip package."""

from __future__ import annotations

from typing import Any

__all__ = ["run"]


def run(*args: Any, **kwargs: Any) -> None:
    """Invoke the GUI entry point lazily to avoid heavy imports on package load."""

    from .app import run as _run

    _run(*args, **kwargs)
