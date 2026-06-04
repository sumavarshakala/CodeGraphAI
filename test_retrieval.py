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

    # SOURCE INFO
    metadata = results["metadatas"][0][i]

    print(
        f"Source: {metadata['file']} "
        f"({metadata['start_line']}-{metadata['end_line']})"
    )

    if metadata.get("symbol"):
        print(f"Symbol: {metadata['symbol']}")

    print()

    print(doc[:500])