from backend.ingestion.clone import clone_repository
from backend.ingestion.reader import read_repository
from backend.chunking.chunker import chunk_files

from backend.embeddings.embedder import embed_texts

repo = clone_repository(
    "https://github.com/psf/requests"
)

data = read_repository(repo.local_path)

chunks = chunk_files(
    repo.repo_id,
    data.files
)

texts = [
    chunk.text
    for chunk in chunks[:10]
]

vectors = embed_texts(texts)

print("Chunks:", len(texts))
print("Vectors:", len(vectors))
print("Dimensions:", len(vectors[0]))