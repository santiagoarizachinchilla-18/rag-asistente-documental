from app.embeddings import generate_embeddings
from app.vector_store import search_similar


def retrieve(question: str, top_k: int = 4) -> list[dict]:
    """Recupera fragmentos relevantes para una pregunta."""

    if not question or not question.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    if top_k <= 0:
        raise ValueError("top_k debe ser mayor que cero.")

    query_embedding = generate_embeddings(
        [question.strip()]
    )[0]

    return search_similar(
        query_embedding=query_embedding,
        top_k=top_k,
    )