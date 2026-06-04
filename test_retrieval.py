from backend.embeddings.embedder import embed_texts
from backend.vectorstore.chroma_store import search

query = "How does authentication work?"

query_vector = embed_texts([query])[0]

results = search(
    query_vector,
    top_k=5
)

print("\nTop Results:\n")

for i, doc in enumerate(results["documents"][0]):
    print("=" * 80)
    print(f"Result {i+1}")
    print(doc[:500])