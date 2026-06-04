from backend.rag.pipeline import (
    index_repository,
    ask_question,
)

print(
    index_repository(
        "https://github.com/psf/requests"
    )
)

print(
    ask_question(
        "How does authentication work?"
    )
)