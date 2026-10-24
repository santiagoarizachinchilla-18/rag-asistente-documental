import pytest

from app import retriever


def test_retrieve_returns_results(monkeypatch):
    expected_results = [
        {
            "chunk_id": "vacaciones_001",
            "source": "politica_vacaciones.md",
            "text": "Los empleados tienen 15 días hábiles.",
            "distance": 0.2,
        }
    ]

    def fake_embeddings(texts):
        assert texts == ["¿Cuántos días de vacaciones hay?"]
        return [[0.1, 0.2, 0.3]]

    def fake_search(query_embedding, top_k):
        assert query_embedding == [0.1, 0.2, 0.3]
        assert top_k == 4
        return expected_results

    monkeypatch.setattr(
        retriever,
        "generate_embeddings",
        fake_embeddings,
    )

    monkeypatch.setattr(
        retriever,
        "search_similar",
        fake_search,
    )

    results = retriever.retrieve(
        "¿Cuántos días de vacaciones hay?"
    )

    assert results == expected_results


def test_retrieve_empty_question():
    with pytest.raises(ValueError):
        retriever.retrieve("   ")


def test_retrieve_invalid_top_k():
    with pytest.raises(ValueError):
        retriever.retrieve("Vacaciones", top_k=0)