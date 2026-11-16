"""Module 1: raw concept -> timed, second-by-second script."""

from __future__ import annotations

import re

from config import get_settings
from core import prompts
from core.llm import LLMClient
from core.models import Script, Segment
from core.timing import retime

# Used when no API key is configured, so the whole pipeline still runs offline.
OFFLINE_BEATS = [
    ("hook", "This is the story nobody saw coming."),
    ("setup", "Here is what was happening before everything changed."),
    ("escalation", "Then it got worse, and much faster than anyone expected."),
    ("twist", "But one unexpected moment shifted everything."),
    ("climax", "In the end, everything came down to a single choice."),
    ("resolution", "This is how it finally ended."),
    ("cta", "Follow for more true stories like this."),
]

OFFLINE_SHOTS = {
    "hook": "dramatic close up",
    "setup": "wide establishing shot",
    "escalation": "storm rising over water",
    "twist": "sudden sharp movement",
    "climax": "hands reaching in tension",
    "resolution": "golden sunrise calm",
    "cta": "person smiling walking outside",
}


def generate_script(
    concept: str,
    niche: str,
    duration: int,
    tone: str,
    hook_style: str,
    llm: LLMClient | None = None,
) -> Script:
    """Write a script with the model, or fall back to an offline template when llm is None."""
    if llm is None:
        script = offline_script(concept, duration)
    else:
        raw = llm.complete_json(
            prompts.SCRIPT_SYSTEM,
            prompts.script_user_prompt(
                concept, niche, duration, tone, hook_style, get_settings().words_per_second
            ),
        )
        script = Script.model_validate(raw)

    if not script.segments:
        raise ValueError("The script came back with no segments.")
    for index, segment in enumerate(script.segments):
        segment.index = index
    retime(script.segments, duration)
    return script


def offline_script(concept: str, duration: int) -> Script:
    """A structural draft built from the concept itself. Useful for testing the pipeline."""
    headline = " ".join(concept.split()).rstrip(".")
    keywords = re.findall(r"[A-Za-z]{4,}", headline)[:2] or ["dramatic", "landscape"]
    segments: list[Segment] = []
    for beat, line in OFFLINE_BEATS:
        segments.append(
            Segment(
                index=len(segments),
                beat=beat,
                narration=f"{line} {headline}." if beat == "hook" else line,
                on_screen_text=headline[:40] if beat == "hook" else "",
                voice_direction="urgent, low, slow start" if beat == "hook"
                else "warm, relaxed" if beat == "cta" else "steady, measured",
                visual_keywords=[*keywords, OFFLINE_SHOTS[beat]],
            )
        )
    return Script(
        title=headline[:60] or "Untitled story",
        hook=segments[0].narration,
        segments=segments,
        hashtags=["#truestory", "#humaninterest", "#shorts"],
    )
