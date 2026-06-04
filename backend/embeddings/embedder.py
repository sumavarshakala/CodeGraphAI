from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model

    if _model is None:
        print("Loading BGE model...")
        _model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    return _model


def embed_texts(texts):
    model = get_model()

    return model.encode(
        texts,
        normalize_embeddings=True
    )