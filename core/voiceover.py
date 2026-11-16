"""Module 2: segments -> voice-generator-ready blocks with emotion and pacing cues."""

from __future__ import annotations

import json
from dataclasses import dataclass

from core.models import Script, VoiceSettings
from core.text import word_count

# Words in a voice direction that call for a more expressive read (lower stability, higher style).
EXPRESSIVE_CUES = (
    "urgent", "tense", "fear", "panic", "desperate", "sad", "grief",
    "shock", "angry", "excited", "triumph", "relief", "whisper",
)

# Bracketed audio tags placed before the line. These follow ElevenLabs v3 style, but check the
# current ElevenLabs docs for the supported list and edit this map to match.
AUDIO_TAGS = {
    "whisper": "[whispers]",
    "sad": "[sad]",
    "grief": "[sad]",
    "excited": "[excited]",
    "triumph": "[excited]",
    "shock": "[gasps]",
    "pause": "[pauses]",
}

SPEECH_TOLERANCE = 1.1  # a block fits if its speech is at most 10% longer than its slot


@dataclass
class VoiceBlock:
    segment_index: int
    beat: str
    start_sec: float
    end_sec: float
    text: str
    tagged_text: str
    direction: str
    speech_seconds: float
    settings: VoiceSettings

    @property
    def allotted_seconds(self) -> float:
        return round(self.end_sec - self.start_sec, 2)

    @property
    def fits(self) -> bool:
        return self.speech_seconds <= self.allotted_seconds * SPEECH_TOLERANCE


def settings_for_direction(direction: str, base: VoiceSettings) -> VoiceSettings:
    """Adjust the base voice settings to match the emotional cue of one block."""
    if any(cue in direction.lower() for cue in EXPRESSIVE_CUES):
        return base.model_copy(update={
            "stability": max(0.0, base.stability - 0.15),
            "style": min(1.0, base.style + 0.2),
        })
    return base.model_copy()


def audio_tags_for(direction: str) -> list[str]:
    lowered = direction.lower()
    tags: list[str] = []
    for cue, tag in AUDIO_TAGS.items():
        if cue in lowered and tag not in tags:
            tags.append(tag)
    return tags


def build_voice_blocks(script: Script, base: VoiceSettings, words_per_second: float) -> list[VoiceBlock]:
    blocks: list[VoiceBlock] = []
    for segment in script.segments:
        text = segment.narration.strip()
        tags = audio_tags_for(segment.voice_direction)
        blocks.append(
            VoiceBlock(
                segment_index=segment.index,
                beat=segment.beat,
                start_sec=segment.start_sec,
                end_sec=segment.end_sec,
                text=text,
                tagged_text=" ".join([*tags, text]),
                direction=segment.voice_direction,
                speech_seconds=round(word_count(text) / words_per_second, 2),
                settings=settings_for_direction(segment.voice_direction, base),
            )
        )
    return blocks


def to_plain_text(blocks: list[VoiceBlock], include_tags: bool) -> str:
    """Readable export: a header per block, then the text to paste into the generator."""
    parts = []
    for block in blocks:
        header = (
            f"# {block.segment_index + 1} {block.beat} | "
            f"{block.start_sec:.1f}-{block.end_sec:.1f}s | {block.direction or 'no direction'}"
        )
        body = block.tagged_text if include_tags else block.text
        parts.append(f"{header}\n{body}")
    return "\n\n".join(parts) + "\n"


def to_elevenlabs_json(blocks: list[VoiceBlock], voice: VoiceSettings, include_tags: bool) -> str:
    """Request bodies shaped for the ElevenLabs text-to-speech endpoint, one per block.

    previous_text and next_text give the neighbouring lines as context so separate clips keep
    a consistent tone when they are rendered one at a time.
    """
    requests = []
    for i, block in enumerate(blocks):
        body: dict = {
            "text": block.tagged_text if include_tags else block.text,
            "model_id": voice.model_id,
            "voice_settings": {
                "stability": round(block.settings.stability, 2),
                "similarity_boost": round(block.settings.similarity_boost, 2),
                "style": round(block.settings.style, 2),
                "use_speaker_boost": block.settings.use_speaker_boost,
            },
        }
        if i > 0:
            body["previous_text"] = blocks[i - 1].text
        if i < len(blocks) - 1:
            body["next_text"] = blocks[i + 1].text
        requests.append({"segment": block.segment_index + 1, "beat": block.beat, "body": body})

    payload = {
        "voice_name": voice.voice_name,
        "endpoint": f"https://api.elevenlabs.io/v1/text-to-speech/{voice.voice_id or '<VOICE_ID>'}",
        "requests": requests,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
