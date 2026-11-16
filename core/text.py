"""Small text helpers shared across modules."""

from __future__ import annotations

import re

_WORD = re.compile(r"\w+(?:['’-]\w+)*")


def word_count(text: str) -> int:
    """Count spoken words, keeping contractions and hyphenated words together."""
    return len(_WORD.findall(text or ""))


def slugify(value: str, fallback: str = "project") -> str:
    """File-name-safe slug that keeps non-ASCII letters (for example Arabic)."""
    slug = re.sub(r"[^\w]+", "-", value.lower()).strip("-")
    return slug or fallback
