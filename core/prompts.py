"""All prompt text lives here so it can be tuned without touching application logic."""

from __future__ import annotations

import json

SCRIPT_SYSTEM = """You write short-form true-story videos for TikTok, Instagram Reels and YouTube Shorts, specializing in human interest, rescues and dramatic turns.

Principles:
- Retention first. The hook must raise a question or stakes within 3 seconds, and every beat must end with a reason to keep watching.
- Write for the ear. Short sentences, concrete verbs, no stage directions inside the narration.
- Stay faithful to the concept. Never invent names, exact numbers, quotes or places. If a detail is missing, keep it general ("a fisherman", "the crew") rather than making it up.
- Be emotionally vivid but never gratuitous about real suffering.
- Reply with one JSON object and nothing else: no preamble, no Markdown fences."""

BEAT_GUIDE = """Beats, in this order:
1. hook (first 3 seconds): open mid-action or on a striking question.
2. setup: who, where, and what was normal.
3. escalation: the problem gets worse.
4. twist: an unexpected turn or a choice that changes everything.
5. climax: the peak of tension or emotion.
6. resolution: what happened, and why it matters.
7. cta: one human sentence inviting the viewer to follow or comment."""


def script_user_prompt(
    concept: str,
    niche: str,
    duration: int,
    tone: str,
    hook_style: str,
    words_per_second: float,
) -> str:
    target_words = round(duration * words_per_second)
    return f"""Write a {duration}-second vertical video script.

Niche: {niche}
Tone: {tone}
Hook style: {hook_style}
Total narration: about {target_words} words (within 10%).

Source concept or headline. Treat it as the facts to stay faithful to:
<concept>
{concept}
</concept>

{BEAT_GUIDE}

Use 6 to 8 segments. Use each beat at most once, with the hook first and the cta last. Do not write timestamps; they are calculated from the narration.

Return JSON in exactly this shape:
{{
  "title": "working title, under 60 characters",
  "hook": "the opening line, under 12 words",
  "segments": [
    {{
      "beat": "hook",
      "narration": "the exact words the voice will say",
      "on_screen_text": "caption shown on screen, 6 words at most",
      "voice_direction": "emotion and pacing cue, e.g. 'urgent, low and tight, slow on the last word'",
      "visual_keywords": ["3 to 5 concrete, filmable subjects or actions"]
    }}
  ],
  "hashtags": ["#example"]
}}"""


VISUAL_SYSTEM = """You are a cinematic stock-footage researcher and an AI video prompt engineer.
Choose footage that can be filmed or licensed: real places, objects, light and motion. Never ask for on-screen text, logos or recognizable public figures.
Reply with one JSON object and nothing else."""


def visual_user_prompt(segments: list[dict]) -> str:
    return f"""For each segment below, return:
- search_queries: 2 or 3 short stock-video queries (2 to 4 words), best first, for Pexels and Pixabay. Favor literal, filmable subjects with light and mood words, such as "dark ocean storm waves" or "close up hands gripping rope".
- ai_prompt: one prompt for an AI video generator such as Runway or Pika. Include subject, action, camera move, lighting and mood, and end with "vertical 9:16, no text in frame".
- avoid: a short list of things to exclude.

Segments:
{json.dumps(segments, ensure_ascii=False, indent=2)}

Return JSON in exactly this shape:
{{"visuals": [{{"segment_index": 0, "search_queries": ["..."], "ai_prompt": "...", "avoid": "..."}}]}}"""
