from sentence_transformers import SentenceTransformer
_model = SentenceTransformer("all-MiniLM-L6-v2")
def embed(sentences):
    return _model.encode(sentences, normalize_embeddings=True)
