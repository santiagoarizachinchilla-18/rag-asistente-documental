from app.retriever import retrieve
from app.llm_client import generate_answer


def ask_question(
    question: str,
    top_k: int = 4,
) -> dict:
    """Ejecuta el flujo RAG completo."""

    contexts = retrieve(
        question=question,
        top_k=top_k,
    )

    result = generate_answer(
        question=question,
        contexts=contexts,
    )

    return {
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"],
    }