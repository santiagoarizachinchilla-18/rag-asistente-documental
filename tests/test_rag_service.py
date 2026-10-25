from app import rag_service


def test_ask_question(monkeypatch):
    expected_contexts = [
        {
            "chunk_id": "vacaciones_001",
            "source": "politica_vacaciones.md",
            "text": "15 días hábiles.",
            "distance": 0.2,
        }
    ]

    def fake_retrieve(question, top_k):
        assert question == "¿Cuántos días de vacaciones?"
        assert top_k == 4
        return expected_contexts

    def fake_generate(question, contexts):
        assert contexts == expected_contexts

        return {
            "answer": "15 días hábiles [1].",
            "sources": [
                {
                    "reference": 1,
                    "source": "politica_vacaciones.md",
                    "chunk_id": "vacaciones_001",
                    "excerpt": "15 días hábiles.",
                    "distance": 0.2,
                }
            ],
        }

    monkeypatch.setattr(
        rag_service,
        "retrieve",
        fake_retrieve,
    )

    monkeypatch.setattr(
        rag_service,
        "generate_answer",
        fake_generate,
    )

    result = rag_service.ask_question(
        "¿Cuántos días de vacaciones?"
    )

    assert result["answer"] == "15 días hábiles [1]."
    assert result["sources"][0]["chunk_id"] == "vacaciones_001"