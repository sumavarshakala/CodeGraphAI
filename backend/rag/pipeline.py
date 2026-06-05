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
from backend.graph.graph_search import (
    find_class,
    find_function,
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
        "stats": data.stats.to_dict(),
    }


def ask_question(
    question: str,
    top_k: int = 10,
):
    """
    Graph search first.
    If not found, fall back to RAG.
    """

    words = question.split()

    for word in words:

        file_path = find_class(word)

        if file_path:
            return {
                "answer": f"{word} is defined in {file_path}",
                "sources": [],
            }

        file_path = find_function(word)

        if file_path:
            return {
                "answer": f"{word} is defined in {file_path}",
                "sources": [],
            }

    query_embedding = embed_texts(
        [question]
    )[0]

    results = search(
        query_embedding,
        top_k=top_k,
    )

    filtered_docs = []
    filtered_meta = []

    for doc, meta in zip(
        results["documents"][0],
        results["metadatas"][0],
    ):

        file_path = meta.get("file", "")

        if "tests/" in file_path:
            continue

        filtered_docs.append(doc)
        filtered_meta.append(meta)

        if len(filtered_docs) == 5:
            break

    context = "\n\n".join(
        doc[:2000]
        for doc in filtered_docs
    )

    prompt = f"""You are a code repository assistant.

    Answer using ONLY the supplied context.

    Provide a detailed explanation.
    Mention important functions, classes, examples, and implementation details when available.

    Context:
    {context}

    Question:
    {question}

    Answer:"""

    answer = generate_answer(
        prompt
    )
    
    print(results["metadatas"][0])

    return {
        "answer": answer,
        "sources": filtered_meta
    }
