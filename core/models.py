"""Domain models. A project is stored as JSON, so these classes are the single source of truth."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator

BEATS: tuple[str, ...] = ("hook", "setup", "escalation", "twist", "climax", "resolution", "cta")


class Stage(str, Enum):
    IDEA = "Idea"
    SCRIPT = "Script"
    VOICEOVER = "Voiceover"
    VISUALS = "Visuals"
    EDITING = "Editing"
    EXPORTED = "Exported"


STAGES: list[Stage] = list(Stage)


def stage_index(stage: Stage) -> int:
    return STAGES.index(stage)


def advance_to(current: Stage, target: Stage) -> Stage:
    """Move a project forward to target. Never moves it backwards."""
    return target if stage_index(target) > stage_index(current) else current


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Segment(BaseModel):
    """One beat of the video: its timing, narration and production cues."""

    index: int = 0
    beat: str = "setup"
    start_sec: float = 0.0
    end_sec: float = 0.0
    narration: str
    on_screen_text: str = ""
    voice_direction: str = ""
    visual_keywords: list[str] = Field(default_factory=list)

    @field_validator("beat", mode="before")
    @classmethod
    def _normalise_beat(cls, value: object) -> str:
        cleaned = str(value or "").strip().lower()
        return cleaned if cleaned in BEATS else "setup"


class Script(BaseModel):
    title: str = "Untitled story"
    hook: str = ""
    segments: list[Segment]
    hashtags: list[str] = Field(default_factory=list)

    @property
    def total_seconds(self) -> float:
        return self.segments[-1].end_sec if self.segments else 0.0


class VisualSuggestion(BaseModel):
    segment_index: int
    search_queries: list[str] = Field(default_factory=list)
    ai_prompt: str = ""
    avoid: str = ""


class VoiceSettings(BaseModel):
    voice_name: str = "My narrator"
    voice_id: str = ""
    model_id: str = "eleven_multilingual_v2"
    stability: float = Field(default=0.5, ge=0.0, le=1.0)
    similarity_boost: float = Field(default=0.75, ge=0.0, le=1.0)
    style: float = Field(default=0.3, ge=0.0, le=1.0)
    use_speaker_boost: bool = True


class Project(BaseModel):
    id: int | None = None
    title: str
    concept: str
    niche: str = "human interest"
    target_duration: int = 45
    stage: Stage = Stage.IDEA
    notes: str = ""
    script: Script | None = None
    visuals: list[VisualSuggestion] = Field(default_factory=list)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
