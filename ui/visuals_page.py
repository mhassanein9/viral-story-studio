"""Module 3 UI: segments -> stock-footage queries, source links and AI video prompts."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.llm import LLMClient
from core.models import Project, Stage, advance_to
from core.storage import ProjectRepository
from core.text import slugify
from core.visuals import build_visual_plan, pexels_url, pixabay_url


def render(repo: ProjectRepository, llm: LLMClient | None, project: Project) -> None:
    st.header("3 · Visuals")
    if project.script is None:
        st.info("Generate a script in module 1 first.")
        return
    st.caption("Stock-footage searches and AI video prompts, one set per beat. The links open each site's search page.")

    if st.button("Build visual plan", type="primary"):
        with st.spinner("Matching footage to each beat..."):
            try:
                plan = build_visual_plan(project.script, llm)
            except Exception as exc:
                st.error(f"Visual plan failed: {exc}")
            else:
                project.visuals = plan
                project.stage = advance_to(project.stage, Stage.VISUALS)
                repo.save(project)
                st.rerun()

    if not project.visuals:
        st.info("No visual plan yet. Build one above.")
        return

    by_index = {v.segment_index: v for v in project.visuals}
    rows: list[dict] = []
    for segment in project.script.segments:
        suggestion = by_index.get(segment.index)
        with st.container(border=True):
            st.markdown(
                f"**{segment.index + 1}. {segment.beat.capitalize()}** · "
                f"{segment.start_sec:.1f}–{segment.end_sec:.1f}s"
            )
            st.caption(segment.narration)
            if suggestion is None:
                st.caption("No suggestion for this beat yet. Rebuild the plan.")
                continue

            for query in suggestion.search_queries:
                st.markdown(f"- `{query}` · [Pexels]({pexels_url(query)}) · [Pixabay]({pixabay_url(query)})")
            st.caption("AI video prompt for Runway or Pika")
            st.code(suggestion.ai_prompt, language=None)
            if suggestion.avoid:
                st.caption(f"Avoid: {suggestion.avoid}")

        rows.append({
            "segment": segment.index + 1,
            "beat": segment.beat,
            "start_s": segment.start_sec,
            "end_s": segment.end_sec,
            "search_queries": " | ".join(suggestion.search_queries),
            "ai_prompt": suggestion.ai_prompt,
            "avoid": suggestion.avoid,
        })

    if rows:
        st.download_button(
            "Download visual plan (CSV)",
            pd.DataFrame(rows).to_csv(index=False),
            file_name=f"{slugify(project.title)}-visuals.csv",
            mime="text/csv",
        )
