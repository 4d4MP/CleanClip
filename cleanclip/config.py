"""Configuration management for CleanClip."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

DEFAULT_PATTERNS: List[Dict[str, str]] = [
    {
        "pattern": r"\b(?:\d[ -]*?){13,16}\b",
        "placeholder": "XXXX-XXXX-XXXX-XXXX",
    },
    {
        "pattern": r"[a-zA-Z0-9._%+-]+@lhsystems\.com",
        "placeholder": "XXXXXXX@lhsystems.com",
    },
    {
        "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "placeholder": "hidden@email.com",
    },
]

CONFIG_DIR = Path.home() / ".cleanclip"
CONFIG_FILE = CONFIG_DIR / "patterns.json"


def ensure_config_dir() -> None:
    """Ensure that the configuration directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_patterns() -> List[Dict[str, str]]:
    """Load patterns from disk or return defaults when unavailable."""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                valid = [
                    item
                    for item in data
                    if isinstance(item, dict)
                    and "pattern" in item
                    and "placeholder" in item
                ]
                if valid:
                    return valid
        except json.JSONDecodeError:
            pass
    save_patterns(DEFAULT_PATTERNS)
    return DEFAULT_PATTERNS


def save_patterns(patterns: List[Dict[str, str]]) -> None:
    """Persist patterns to disk."""
    ensure_config_dir()
    CONFIG_FILE.write_text(
        json.dumps(patterns, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def serialize_patterns(patterns: List[Dict[str, str]]) -> str:
    """Convert patterns to an editable text representation."""
    lines = [
        "# One pattern per line using the format: <regex> -> <placeholder>",
        "# Lines starting with # are ignored.",
    ]
    for entry in patterns:
        pattern = entry["pattern"]
        placeholder = entry["placeholder"]
        lines.append(f"{pattern} -> {placeholder}")
    return "\n".join(lines)


def parse_patterns_text(text: str) -> List[Dict[str, str]]:
    """Parse patterns from the editable text representation."""
    import re

    patterns: List[Dict[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "->" not in line:
            raise ValueError(
                "Each non-comment line must contain '->' separating pattern and placeholder."
            )
        pattern_part, placeholder_part = (
            segment.strip() for segment in line.split("->", maxsplit=1)
        )
        if not pattern_part or not placeholder_part:
            raise ValueError("Pattern and placeholder cannot be empty.")
        pattern = pattern_part.strip("'\"")
        placeholder = placeholder_part.strip("'\"")
        try:
            re.compile(pattern)
        except re.error as exc:  # pragma: no cover - defensive branch
            raise ValueError(f"Invalid regular expression '{pattern}': {exc}") from exc
        patterns.append({"pattern": pattern, "placeholder": placeholder})
    if not patterns:
        raise ValueError("At least one pattern must be provided.")
    return patterns
