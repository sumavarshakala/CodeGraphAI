from backend.embeddings.embedder import embed_texts
from backend.vectorstore.chroma_store import search
from backend.llm.ollama_client import generate_answer

question = "How does authentication work in this repository?"

query_vector = embed_texts([question])[0]

results = search(
    query_vector,
    top_k=5,
)

context = "\n\n".join(
    results["documents"][0]
)

prompt = f"""
You are a code assistant.

Answer using ONLY the provided context.

Context:
{context}

Question:
{question}

Answer:
"""

answer = generate_answer(prompt)

print(answer)