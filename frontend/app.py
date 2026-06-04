"""
Streamlit UI for CodeGraphAI.

Changes vs original:
- st.session_state guards prevent re-indexing on every widget rerun.
- Index result persists across reruns (stored in session state).
- Errors from ask_question() are shown via st.error(), never as crashes.
- Input validation before firing expensive operations.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import streamlit as st

from backend.rag.pipeline import ask_question, index_repository

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


st.set_page_config(
    page_title="CodeGraphAI",
    layout="wide",
)

st.title("CodeGraphAI")

# ── Session state initialisation ──────────────────────────────────────────────
if "indexed_repo" not in st.session_state:
    st.session_state.indexed_repo = None    # last successfully indexed URL
if "index_result" not in st.session_state:
    st.session_state.index_result = None    # {repo_id, files, chunks}

# ── Repository indexing ───────────────────────────────────────────────────────
repo_url = st.text_input("GitHub Repository URL")

if st.button("Index Repository"):
    if not repo_url.strip():
        st.warning("Please enter a repository URL.")
    else:
        with st.spinner("Cloning and indexing repository…"):
            try:
                result = index_repository(repo_url.strip())
                st.session_state.indexed_repo = repo_url.strip()
                st.session_state.index_result = result
            except Exception as exc:
                st.error(f"Indexing failed: {exc}")

if st.session_state.index_result:
    r = st.session_state.index_result

    st.success("✅ Repository Indexed Successfully")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Files Indexed", r["files"])

    with col2:
        st.metric("Chunks Generated", r["chunks"])

    st.info(
    f"""
    Repository: {r['repo_id']}
    """
    )

st.divider()

# ── Question answering ────────────────────────────────────────────────────────
question = st.text_input("Ask a Question")

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching and thinking…"):
            result = ask_question(question.strip())

        if result.get("error"):
            st.error(f"⚠️ {result['error']}")

        else:
            st.session_state.chat_history.append(
                {
                    "question": question,
                    "answer": result["answer"],
                    "sources": result["sources"]
                }
            )

for chat in reversed(st.session_state.chat_history):

    st.markdown("### 🙋 Question")
    st.write(chat["question"])

    st.markdown("### 🤖 Answer")
    st.write(chat["answer"])

    with st.expander("📚 Sources Used"):

        for source in chat["sources"]:

            st.markdown(
                f"""
**File:** `{source['file']}`

**Lines:** {source['start_line']} - {source['end_line']}

**Symbol:** {source.get('symbol', 'N/A')}
"""
            )

    st.divider()