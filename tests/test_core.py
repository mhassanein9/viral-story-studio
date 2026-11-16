"""Unit tests for the pure logic and storage. Run with: pytest"""

import pytest

from core.llm import LLMError, extract_json
from core.models import Project, Stage, VoiceSettings
from core.script_generator import generate_script
from core.storage import ProjectRepository
from core.visuals import build_visual_plan, pexels_url
from core.voiceover import build_voice_blocks, settings_for_direction

CONCEPT = "A dog breaks through the ice to save a boy, and a stranger throws a rope"


def make_script(duration: int = 45):
    return generate_script(CONCEPT, "human interest", duration, "Urgent and gripping", "Open mid-action", llm=None)


def test_extract_json_handles_fences_and_prose():
    reply = 'Sure, here it is:\n```json\n{"title": "A"}\n```\nEnjoy!'
    assert extract_json(reply) == {"title": "A"}


def test_extract_json_rejects_text_without_json():
    with pytest.raises(LLMError):
        extract_json("no JSON in this reply")


def test_timing_is_contiguous_and_covers_target():
    segments = make_script(45).segments
    assert segments[0].start_sec == 0
    assert segments[-1].end_sec == 45
    for prev, cur in zip(segments, segments[1:]):
        assert cur.start_sec == pytest.approx(prev.end_sec)


def test_offline_script_starts_with_hook_and_ends_with_cta():
    script = make_script()
    assert script.segments[0].beat == "hook"
    assert script.segments[-1].beat == "cta"


def test_repository_round_trip(tmp_path):
    repo = ProjectRepository(tmp_path / "test.db")
    project = repo.save(Project(title="Test", concept=CONCEPT))
    assert project.id is not None

    project.script = make_script(30)
    project.stage = Stage.SCRIPT
    repo.save(project)

    loaded = repo.get(project.id)
    assert loaded.stage == Stage.SCRIPT
    assert loaded.script.total_seconds == 30

    repo.delete(project.id)
    assert repo.get(project.id) is None


def test_expressive_direction_lowers_stability_and_raises_style():
    base = VoiceSettings(stability=0.5, style=0.3)
    expressive = settings_for_direction("urgent, whispered", base)
    calm = settings_for_direction("calm and steady", base)
    assert expressive.stability < calm.stability
    assert expressive.style > calm.style


def test_whisper_direction_adds_audio_tag():
    script = make_script()
    script.segments[0].voice_direction = "whispered, slow"
    blocks = build_voice_blocks(script, VoiceSettings(), words_per_second=2.6)
    assert blocks[0].tagged_text.startswith("[whispers]")
    assert len(blocks) == len(script.segments)


def test_visual_plan_covers_every_segment_offline():
    script = make_script()
    plan = build_visual_plan(script, llm=None)
    assert [v.segment_index for v in plan] == [s.index for s in script.segments]
    assert all(v.search_queries for v in plan)


def test_pexels_url_is_slugged():
    assert pexels_url("Dark Ocean Waves") == "https://www.pexels.com/search/videos/dark-ocean-waves/"
