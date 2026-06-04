from backend.ingestion.clone import clone_repository
from backend.ingestion.reader import read_repository
from backend.chunking.chunker import chunk_files

repo = clone_repository(
    "https://github.com/psf/requests"
)

data = read_repository(repo.local_path)

chunks = chunk_files(
    repo.repo_id,
    data.files
)

print("Total Chunks:", len(chunks))

for chunk in chunks:
    if chunk.language == "python":
        print("=" * 60)
        print("File:", chunk.relative_path)
        print("Symbol:", chunk.symbol)
        print("Lines:", chunk.start_line, "-", chunk.end_line)

        if chunk.symbol:
            break