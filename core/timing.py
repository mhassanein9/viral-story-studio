"""Segment timing. Each beat's length follows how long its narration takes to say."""

from __future__ import annotations

from core.models import Script, Segment
from core.text import word_count

# Minimum weight per beat (about 2.5 seconds of speech) so short lines stay on screen long enough.
MIN_SEGMENT_WEIGHT = 6


def retime(segments: list[Segment], total_seconds: float) -> list[Segment]:
    """Lay segments back to back so they cover exactly [0, total_seconds]."""
    if not segments:
        return segments
    weights = [max(MIN_SEGMENT_WEIGHT, word_count(s.narration)) for s in segments]
    scale = total_seconds / sum(weights)
    cursor = 0.0
    for segment, weight in zip(segments, weights):
        segment.start_sec = round(cursor, 2)
        cursor += weight * scale
        segment.end_sec = round(cursor, 2)
    segments[-1].end_sec = float(total_seconds)
    return segments


def script_speaking_seconds(script: Script, words_per_second: float) -> float:
    """Estimated time to speak the whole narration at the given speaking rate."""
    words = sum(word_count(s.narration) for s in script.segments)
    return words / words_per_second
