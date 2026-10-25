from fastapi.testclient import TestClient

from app import main


client = TestClient(main.app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask(monkeypatch):
    expected = {
        "question": "¿Cuántos días de vacaciones?",
        "answer": "Los empleados tienen 15 días hábiles [1].",
        "sources": [
            {
                "reference": 1,
                "source": "politica_vacaciones.md",
                "chunk_id": "politica_vacaciones_001",
                "excerpt": "Los empleados tienen 15 días hábiles.",
                "distance": 0.2,
            }
        ],
    }

    def fake_ask_question(question, top_k):
        assert question == expected["question"]
        assert top_k == 4
        return expected

    monkeypatch.setattr(
        main,
        "ask_question",
        fake_ask_question,
    )

    response = client.post(
        "/ask",
        json={
            "question": expected["question"],
            "top_k": 4,
        },
    )

    assert response.status_code == 200
    assert response.json() == expected


def test_ask_empty_question():
    response = client.post(
        "/ask",
        json={"question": "   ", "top_k": 4},
    )

    assert response.status_code == 422


def test_ask_invalid_top_k():
    response = client.post(
        "/ask",
        json={"question": "Vacaciones", "top_k": 0},
    )

    assert response.status_code == 422