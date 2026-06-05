from backend.graph.graph_builder import (
    add_file_graph,
)

symbols = {
    "classes": ["User"],
    "functions": ["login", "logout"],
    "imports": ["requests", "os"],
}

add_file_graph(
    repo_name="psf_requests",
    file_path="auth.py",
    symbols=symbols,
)

print("Graph created")