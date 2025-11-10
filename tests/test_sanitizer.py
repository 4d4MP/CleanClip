"""Unit tests for sanitizer helpers."""

from cleanclip.sanitizer import sanitize_text, has_sensitive_data
from cleanclip.config import DEFAULT_PATTERNS


def test_sanitize_replaces_email():
    text = "Contact us at example@lhsystems.com for support."
    sanitized = sanitize_text(text, DEFAULT_PATTERNS)
    assert "XXXXXXX@lhsystems.com" in sanitized
    assert "example@lhsystems.com" not in sanitized


def test_sanitize_replaces_credit_card_like_sequence():
    text = "Payment info: 1234-5678-9012-3456"
    sanitized = sanitize_text(text, DEFAULT_PATTERNS)
    assert "XXXX-XXXX-XXXX-XXXX" in sanitized


def test_has_sensitive_data_detects_change():
    original = "foo"
    sanitized = "bar"
    assert has_sensitive_data(original, sanitized)


def test_has_sensitive_data_detects_no_change():
    original = "foo"
    sanitized = "foo"
    assert not has_sensitive_data(original, sanitized)
