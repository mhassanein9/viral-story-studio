"""Module 2 UI: segments -> voice-generator-ready blocks with emotion and pacing cues."""

from __future__ import annotations

import streamlit as st

from config import get_settings
from core.models import Project, Stage, VoiceSettings, advance_to
from core.storage import ProjectRepository
from core.text import slugify
from core.voiceover import build_voice_blocks, to_elevenlabs_json, to_plain_text


def render(repo: ProjectRepository, project: Project) -> None:
    st.header("2 · Voiceover")
    if project.script is None:
        st.info("Generate a script in module 1 first.")
        return
    st.caption("One block per beat. Copy a block into your voice generator, render it, and keep the file with the project.")

    _voice_profile_form(repo, project)

    include_tags = st.toggle(
        "Include audio tags",
        value=False,
        help="Adds cues such as [whispers] before the line. Turn this on only for a model that reads audio tags.",
    )
    blocks = build_voice_blocks(project.script, project.voice, get_settings().words_per_second)

    for block in blocks:
        with st.container(border=True):
            fit = "fits its slot" if block.fits else "runs long, trim it"
            st.markdown(
                f"**{block.segment_index + 1}. {block.beat.capitalize()}** · "
                f"{block.start_sec:.1f}–{block.end_sec:.1f}s · "
                f"speech about {block.speech_seconds:.1f}s of {block.allotted_seconds:.1f}s ({fit})"
            )
            st.caption(
                f"Direction: {block.direction or 'none'} · "
                f"stability {block.settings.stability:.2f} · style {block.settings.style:.2f}"
            )
            st.code(block.tagged_text if include_tags else block.text, language=None)

    st.markdown("#### Export")
    slug = slugify(project.title)
    c1, c2 = st.columns(2)
    c1.download_button(
        "Text blocks (.txt)",
        to_plain_text(blocks, include_tags),
        file_name=f"{slug}-voiceover.txt",
        mime="text/plain",
    )
    c2.download_button(
        "ElevenLabs requests (.json)",
        to_elevenlabs_json(blocks, project.voice, include_tags),
        file_name=f"{slug}-elevenlabs.json",
        mime="application/json",
    )

    if st.button("Mark voiceover done"):
        project.stage = advance_to(project.stage, Stage.VOICEOVER)
        repo.save(project)
        st.rerun()


def _voice_profile_form(repo: ProjectRepository, project: Project) -> None:
    voice = project.voice
    with st.expander("Voice profile", expanded=not voice.voice_id):
        with st.form("voice_profile"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Voice name", value=voice.voice_name)
            voice_id = c2.text_input(
                "ElevenLabs voice ID",
                value=voice.voice_id,
                help="Copy it from your ElevenLabs voice library. You can leave it blank for now.",
            )
            model_id = st.text_input(
                "Model ID",
                value=voice.model_id,
                help="For example eleven_multilingual_v2. Check ElevenLabs for the current list.",
            )
            s1, s2, s3, s4 = st.columns(4)
            stability = s1.slider(
                "Stability", 0.0, 1.0, voice.stability, 0.05,
                help="Lower values give a wider emotional range and more variation between takes.",
            )
            similarity = s2.slider(
                "Similarity", 0.0, 1.0, voice.similarity_boost, 0.05,
                help="How closely the output sticks to the original voice.",
            )
            style = s3.slider(
                "Style", 0.0, 1.0, voice.style, 0.05,
                help="Exaggerates the delivery. Keep it low for calm narration.",
            )
            speaker = s4.checkbox("Speaker boost", value=voice.use_speaker_boost)

            if st.form_submit_button("Save voice profile"):
                project.voice = VoiceSettings(
                    voice_name=name.strip() or "My narrator",
                    voice_id=voice_id.strip(),
                    model_id=model_id.strip() or voice.model_id,
                    stability=stability,
                    similarity_boost=similarity,
                    style=style,
                    use_speaker_boost=speaker,
                )
                repo.save(project)
                st.rerun()
