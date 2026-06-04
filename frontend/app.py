import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import streamlit as st

from backend.rag.pipeline import (
    index_repository,
    ask_question,
)

st.set_page_config(
    page_title="CodeGraphAI",
    layout="wide",
)

st.title("CodeGraphAI")

repo_url = st.text_input(
    "GitHub Repository URL"
)

if st.button("Index Repository"):
    with st.spinner("Indexing repository..."):
        result = index_repository(repo_url)

    st.success(
        f"Indexed {result['chunks']} chunks from {result['files']} files"
    )

question = st.text_input(
    "Ask a Question"
)

if st.button("Ask"):
    with st.spinner("Thinking..."):
        answer = ask_question(question)

    st.write(answer)