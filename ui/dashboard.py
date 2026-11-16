"""Dashboard: pipeline overview, new projects, and stage tracking for the active project."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from config import get_settings
from core.models import STAGES, Project, stage_index
from core.storage import ProjectRepository
from ui.state import PENDING_KEY


def render(repo: ProjectRepository, active: Project | None) -> None:
    st.header("Dashboard")
    st.caption("Track each video from idea to export.")

    projects = repo.list_projects()
    columns = st.columns(len(STAGES))
    for column, stage in zip(columns, STAGES):
        column.metric(stage.value, sum(p.stage == stage for p in projects))

    _new_project_form(repo, has_projects=bool(projects))

    st.subheader("All projects")
    if not projects:
        st.info("No projects yet. Create one above to start the pipeline.")
    else:
        last = len(STAGES) - 1
        table = pd.DataFrame([
            {
                "Title": p.title,
                "Stage": p.stage.value,
                "Progress": round(stage_index(p.stage) / last * 100),
                "Target": f"{p.target_duration}s",
                "Updated": p.updated_at.strftime("%Y-%m-%d %H:%M"),
            }
            for p in projects
        ])
        st.dataframe(
            table,
            hide_index=True,
            column_config={
                "Progress": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d%%"),
            },
        )

    st.subheader("Active project")
    if active is None:
        st.info("Pick a project in the sidebar to manage its stage and notes.")
        return
    _stage_controls(repo, active)


def _new_project_form(repo: ProjectRepository, has_projects: bool) -> None:
    settings = get_settings()
    with st.expander("New project", expanded=not has_projects):
        with st.form("new_project"):
            title = st.text_input("Working title", placeholder="Dog pulled from a frozen lake")
            concept = st.text_area(
                "Raw concept or headline",
                height=110,
                placeholder="A man breaks through the ice to reach his dog. A stranger ...",
            )
            c1, c2 = st.columns(2)
            niche = c1.text_input("Niche", value="human interest")
            duration = c2.slider("Target length (seconds)", 20, 90, settings.default_duration, step=5)
            submitted = st.form_submit_button("Create project", type="primary")

    if submitted:
        if not title.strip() or not concept.strip():
            st.error("Add a working title and a concept to create the project.")
            return
        project = repo.save(Project(
            title=title.strip(),
            concept=concept.strip(),
            niche=niche.strip() or "human interest",
            target_duration=duration,
        ))
        st.session_state[PENDING_KEY] = project.id
        st.rerun()


def _stage_controls(repo: ProjectRepository, project: Project) -> None:
    index = stage_index(project.stage)
    last = len(STAGES) - 1
    st.markdown(f"**{project.title}** is in **{project.stage.value}** (step {index + 1} of {len(STAGES)})")

    b1, b2, _ = st.columns([1, 1, 4])
    if b1.button("Previous stage", disabled=index == 0, key="prev_stage"):
        project.stage = STAGES[index - 1]
        repo.save(project)
        st.rerun()
    if b2.button("Next stage", type="primary", disabled=index == last, key="next_stage"):
        project.stage = STAGES[index + 1]
        repo.save(project)
        st.rerun()

    notes = st.text_area(
        "Notes",
        value=project.notes,
        key=f"notes_{project.id}",
        placeholder="Hook recorded? Footage licensed? Caption style?",
    )
    if st.button("Save notes", key=f"save_notes_{project.id}"):
        project.notes = notes
        repo.save(project)
        st.success("Notes saved.")

    with st.expander("Delete project"):
        confirm = st.checkbox(
            "I understand this removes the script, voice settings and visual plan.",
            key=f"confirm_delete_{project.id}",
        )
        if st.button("Delete project", disabled=not confirm, key=f"delete_{project.id}"):
            repo.delete(project.id)
            st.rerun()
