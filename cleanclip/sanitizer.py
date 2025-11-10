"""Utilities for scrubbing sensitive information from text."""

from __future__ import annotations

import re
from typing import Iterable, Dict


def sanitize_text(text: str, patterns: Iterable[Dict[str, str]]) -> str:
    """Replace all occurrences that match the given patterns."""
    sanitized = text
    protected_values: set[str] = set()
    for entry in patterns:
        pattern = entry.get("pattern", "")
        placeholder = entry.get("placeholder", "")
        if not pattern:
            continue
        regex = re.compile(pattern, flags=re.MULTILINE)

        def _replace(match: re.Match[str]) -> str:
            value = match.group(0)
            if value in protected_values:
                return value
            protected_values.add(placeholder)
            return placeholder

        sanitized = regex.sub(_replace, sanitized)
    return sanitized


def has_sensitive_data(original: str, sanitized: str) -> bool:
    """Return True when sanitizing changed the text."""
    return original != sanitized


def apply_sanitization(text: str, patterns: Iterable[Dict[str, str]]) -> str:
    """Convenience function to sanitize when text may be None."""
    if text is None:
        return ""
    return sanitize_text(text, patterns)
