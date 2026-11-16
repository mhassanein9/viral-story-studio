"""Story Reel Studio: Streamlit entry point. Start it with: streamlit run app.py"""

from __future__ import annotations

import streamlit as st

from config import get_settings
from core.llm import LLMClient, LLMError
from core.storage import ProjectRepository
from ui import dashboard, script_page, visuals_page, voice_page
from ui.state import PENDING_KEY, PICKER_KEY

st.set_page_config(page_title="Story Reel Studio", page_icon="🎬", layout="wide")

PAGES = ["Dashboard", "1 · Script", "2 · Voiceover", "3 · Visuals"]


@st.cache_resource
def get_repository() -> ProjectRepository:
    return ProjectRepository(get_settings().db_path)


@st.cache_resource
def get_llm() -> LLMClient | None:
    settings = get_settings()
    if not settings.anthropic_api_key:
        return None
    try:
        return LLMClient(settings.anthropic_api_key, settings.anthropic_model)
    except LLMError:
        return None


repo = get_repository()
llm = get_llm()

# The dashboard can create a project and ask the picker to select it. That must happen
# before the picker widget is drawn, so it is applied here at the top of the run.
if PENDING_KEY in st.session_state:
    st.session_state[PICKER_KEY] = st.session_state.pop(PENDING_KEY)

projects = repo.list_projects()
project_ids = [p.id for p in projects]
if st.session_state.get(PICKER_KEY) not in project_ids:
    st.session_state.pop(PICKER_KEY, None)

with st.sidebar:
    st.title("🎬 Story Reel Studio")
    page = st.radio("Module", PAGES, label_visibility="collapsed")
    st.divider()
    if projects:
        labels = {p.id: f"{p.title} · {p.stage.value}" for p in projects}
        active_id = st.selectbox(
            "Active project", project_ids, format_func=labels.__getitem__, key=PICKER_KEY
        )
    else:
        active_id = None
        st.caption("No projects yet.")

    if llm is None:
        st.warning("Claude is not configured. Using offline templates. Add ANTHROPIC_API_KEY to .env.")
    else:
        st.caption(f"Model: {get_settings().anthropic_model}")

active = repo.get(active_id) if active_id is not None else None

if page == "Dashboard":
    dashboard.render(repo, active)
elif active is None:
    st.info("Create a project on the Dashboard to start.")
elif page == "1 · Script":
    script_page.render(repo, llm, active)
elif page == "2 · Voiceover":
    voice_page.render(repo, active)
else:
    visuals_page.render(repo, llm, active)
