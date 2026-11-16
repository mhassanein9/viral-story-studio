"""Module 1 UI: concept in, timed second-by-second script out."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from config import get_settings
from core.llm import LLMClient
from core.models import Project, Stage, advance_to
from core.script_generator import generate_script
from core.storage import ProjectRepository
from core.text import slugify
from core.timing import retime, script_speaking_seconds

TONES = ["Urgent and gripping", "Warm and hopeful", "Tense and cinematic", "Heartbreaking", "Triumphant"]
HOOK_STYLES = ["Open mid-action", "Ask a question", "Lead with the outcome", "Promise a twist"]


def render(repo: ProjectRepository, llm: LLMClient | None, project: Project) -> None:
    settings = get_settings()
    st.header("1 · Script")
    st.caption("Turn a raw concept into a timed script. Edit any line, then save.")

    with st.form("script_form"):
        concept = st.text_area("Raw concept or headline", value=project.concept, height=120)
        c1, c2, c3 = st.columns(3)
        niche = c1.text_input("Niche", value=project.niche)
        duration = c2.slider("Target length (seconds)", 20, 90, project.target_duration, step=5)
        tone = c3.selectbox("Tone", TONES)
        hook_style = st.selectbox("Hook style", HOOK_STYLES)
        generate = st.form_submit_button("Generate script", type="primary")

    if generate:
        if not concept.strip():
            st.error("Write a concept or headline first.")
        else:
            with st.spinner("Writing beats, narration and timing..."):
                try:
                    script = generate_script(concept.strip(), niche.strip(), duration, tone, hook_style, llm)
                except Exception as exc:  # show model or validation errors instead of crashing
                    st.error(f"Script generation failed: {exc}")
                else:
                    project.concept = concept.strip()
                    project.niche = niche.strip() or project.niche
                    project.target_duration = duration
                    project.script = script
                    project.visuals = []  # the old visual plan no longer matches the script
                    project.stage = advance_to(project.stage, Stage.SCRIPT)
                    repo.save(project)
                    st.rerun()

    if project.script is None:
        st.info("No script yet. Generate one above.")
        return

    script = project.script
    target = project.target_duration
    speaking = script_speaking_seconds(script, settings.words_per_second)

    st.subheader(script.title)
    st.markdown(f"**Hook:** {script.hook}")
    m1, m2, m3 = st.columns(3)
    m1.metric("Target length", f"{target}s")
    m2.metric("Estimated speaking time", f"{speaking:.0f}s")
    m3.metric("Beats", len(script.segments))
    if speaking > target * 1.05:
        st.warning(
            f"The narration is about {speaking - target:.0f}s over the target. "
            "Trim some lines, or raise the target length."
        )
    elif speaking < target * 0.8:
        st.info("The narration is short for this target. Add detail, or shorten the target to keep the pacing tight.")

    st.markdown("#### Timeline")
    st.caption("Edit narration, captions, directions and keywords directly. Timing is recalculated on save.")
    frame = pd.DataFrame([
        {
            "Time": f"{seg.start_sec:.1f}–{seg.end_sec:.1f}s",
            "Beat": seg.beat,
            "Narration": seg.narration,
            "On-screen text": seg.on_screen_text,
            "Voice direction": seg.voice_direction,
            "Visual keywords": ", ".join(seg.visual_keywords),
        }
        for seg in script.segments
    ])
    edited = st.data_editor(
        frame,
        hide_index=True,
        num_rows="fixed",
        key=f"timeline_{project.id}_{int(project.updated_at.timestamp())}",
        column_config={
            "Time": st.column_config.TextColumn(disabled=True),
            "Beat": st.column_config.TextColumn(disabled=True),
        },
    )
    if st.button("Save edits"):
        for seg, row in zip(script.segments, edited.to_dict("records")):
            seg.narration = str(row["Narration"]).strip()
            seg.on_screen_text = str(row["On-screen text"]).strip()
            seg.voice_direction = str(row["Voice direction"]).strip()
            seg.visual_keywords = [k.strip() for k in str(row["Visual keywords"]).split(",") if k.strip()]
        retime(script.segments, target)
        repo.save(project)
        st.rerun()

    st.markdown("#### Export")
    slug = slugify(project.title)
    full_text = "\n\n".join(seg.narration for seg in script.segments)
    c1, c2 = st.columns(2)
    c1.download_button(
        "Script (JSON)",
        script.model_dump_json(indent=2),
        file_name=f"{slug}-script.json",
        mime="application/json",
    )
    c2.download_button(
        "Narration (.txt)",
        full_text,
        file_name=f"{slug}-narration.txt",
        mime="text/plain",
    )
    if script.hashtags:
        st.caption(" ".join(script.hashtags))
