"""Module 3: segments -> stock-footage queries, source links and AI video prompts."""

from __future__ import annotations

import re

from core import prompts
from core.llm import LLMClient
from core.models import Script, VisualSuggestion

BEAT_MOOD = {
    "hook": "high contrast, sudden motion",
    "setup": "warm, calm, documentary feel",
    "escalation": "darkening light, rising tension",
    "twist": "sharp, unsettling framing",
    "climax": "intense backlight, dramatic shadows",
    "resolution": "soft golden light, relief",
    "cta": "clean, hopeful, simple framing",
}


def _url_slug(query: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")


def pexels_url(query: str) -> str:
    return f"https://www.pexels.com/search/videos/{_url_slug(query)}/"


def pixabay_url(query: str) -> str:
    return f"https://pixabay.com/videos/search/{_url_slug(query)}/"


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        cleaned = item.strip()
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            result.append(cleaned)
    return result


def heuristic_suggestion(segment_index: int, beat: str, keywords: list[str]) -> VisualSuggestion:
    """Offline plan built from the segment's own keywords and the beat's mood."""
    keywords = [k for k in keywords if k.strip()] or ["dramatic landscape"]
    queries = _unique([" ".join(keywords[:2]), keywords[0], f"{keywords[-1]} cinematic"])
    return VisualSuggestion(
        segment_index=segment_index,
        search_queries=queries,
        ai_prompt=(
            f"Cinematic vertical 9:16 shot of {', '.join(keywords)}, "
            f"{BEAT_MOOD.get(beat, 'natural light')}, slow camera move, "
            "shallow depth of field, no text in frame"
        ),
        avoid="readable text, logos, identifiable faces",
    )


def build_visual_plan(script: Script, llm: LLMClient | None = None) -> list[VisualSuggestion]:
    """One suggestion per segment. The model refines the heuristic plan when it is available."""
    plan = {
        s.index: heuristic_suggestion(s.index, s.beat, s.visual_keywords)
        for s in script.segments
    }
    if llm is not None:
        payload = [
            {
                "segment_index": s.index,
                "beat": s.beat,
                "narration": s.narration,
                "visual_keywords": s.visual_keywords,
            }
            for s in script.segments
        ]
        raw = llm.complete_json(prompts.VISUAL_SYSTEM, prompts.visual_user_prompt(payload))
        items = raw.get("visuals", []) if isinstance(raw, dict) else []
        for item in items:
            try:
                suggestion = VisualSuggestion.model_validate(item)
            except ValueError:
                continue  # keep the heuristic suggestion for this segment
            if suggestion.segment_index in plan:
                plan[suggestion.segment_index] = suggestion
    return [plan[i] for i in sorted(plan)]
