import chromadb

client = chromadb.PersistentClient(
    path="data/chroma"
)

collection = client.get_or_create_collection(
    name="code_chunks"
)

def store_chunks(chunks, embeddings):
    collection.add(
        ids=[c.chunk_id for c in chunks],
        documents=[c.text for c in chunks],
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "file": c.relative_path,
                "language": c.language,
                "symbol": c.symbol or "",
                "start_line": c.start_line,
                "end_line": c.end_line,
            }
            for c in chunks
        ],
    )
def search(query_embedding, top_k=5):
    return collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )

def count_chunks():
    return collection.count()