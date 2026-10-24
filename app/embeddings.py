from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Carga el modelo una sola vez por proceso."""
    return SentenceTransformer(MODEL_NAME)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Convierte los textos en vectores numéricos."""

    if not texts:
        return []

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return vectors.tolist()