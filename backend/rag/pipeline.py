from backend.ingestion.clone import clone_repository
from backend.ingestion.reader import read_repository
from backend.chunking.chunker import chunk_files

from backend.embeddings.embedder import embed_texts

from backend.vectorstore.chroma_store import (
    store_chunks,
    search,
)

from backend.llm.ollama_client import (
    generate_answer,
)


def index_repository(repo_url: str):
    """
    Clone repo and build vector index.
    """

    repo = clone_repository(repo_url)

    data = read_repository(repo.local_path)

    chunks = chunk_files(
        repo.repo_id,
        data.files,
    )

    texts = [
        chunk.text
        for chunk in chunks
    ]

    embeddings = embed_texts(texts)

    store_chunks(
        chunks,
        embeddings,
    )

    return {
        "repo_id": repo.repo_id,
        "files": len(data.files),
        "chunks": len(chunks),
    }


def ask_question(
    question: str,
    top_k: int = 5,
):
    """
    Retrieve relevant chunks and ask Qwen.
    """

    query_embedding = embed_texts(
        [question]
    )[0]

    results = search(
        query_embedding,
        top_k=top_k,
    )

    context = "\n\n".join(
        results["documents"][0]
    )

    prompt = f"""
You are a code repository assistant.

Answer ONLY from the supplied context.

Context:
{context}

Question:
{question}

Answer:
"""

    answer = generate_answer(
        prompt
    )

    return answer