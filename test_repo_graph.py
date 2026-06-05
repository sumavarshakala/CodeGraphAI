from backend.ingestion.reader import read_repository
from backend.graph.graph_extractor import (
    extract_python_symbols,
)
from backend.graph.graph_builder import (
    add_file_graph,
)

from pathlib import Path

repo_path = Path("data/repos/psf_requests")

data = read_repository(repo_path)

count = 0

for file in data.files:

    if file.language != "python":
        continue

    try:
        symbols = extract_python_symbols(
            file.text
        )

        add_file_graph(
            repo_name="psf_requests",
            file_path=file.relative_path,
            symbols=symbols,
        )

        count += 1

    except Exception:
        pass

print(f"Processed {count} Python files")