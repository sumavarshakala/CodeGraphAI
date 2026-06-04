from backend.ingestion.clone import clone_repository
from backend.ingestion.reader import read_repository
from backend.chunking.chunker import chunk_files
from backend.embeddings.embedder import embed_texts
from backend.vectorstore.chroma_store import (
    store_chunks,
    count_chunks,
)

repo = clone_repository(
    "https://github.com/psf/requests"
)

data = read_repository(
    repo.local_path
)

chunks = chunk_files(
    repo.repo_id,
    data.files
)

texts = [chunk.text for chunk in chunks]

vectors = embed_texts(texts)

store_chunks(
    chunks,
    vectors
)

print("Stored Chunks:", count_chunks())