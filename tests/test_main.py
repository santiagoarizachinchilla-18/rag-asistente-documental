from types import SimpleNamespace

import httpx
from fastapi.testclient import TestClient
from openai import APIConnectionError

from app import main


client = TestClient(main.app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index(monkeypatch):
    documents = [
        {
            "source": "documento.md",
            "text": "Contenido de prueba.",
        }
    ]

    chunks = [
        {
            "chunk_id": "documento_001",
            "source": "documento.md",
            "text": "Contenido de prueba.",
        }
    ]

    embeddings = [[0.1, 0.2, 0.3]]

    def fake_load_documents(directory):
        assert directory == main.Path("documents")
        return documents

    def fake_chunk_documents(loaded_documents):
        assert loaded_documents == documents
        return chunks

    def fake_generate_embeddings(texts):
        assert texts == ["Contenido de prueba."]
        return embeddings

    def fake_index_chunks(received_chunks, received_embeddings):
        assert received_chunks == chunks
        assert received_embeddings == embeddings
        return 1

    monkeypatch.setattr(
        main,
        "load_documents",
        fake_load_documents,
    )

    monkeypatch.setattr(
        main,
        "chunk_documents",
        fake_chunk_documents,
    )

    monkeypatch.setattr(
        main,
        "generate_embeddings",
        fake_generate_embeddings,
    )

    monkeypatch.setattr(
        main,
        "index_chunks",
        fake_index_chunks,
    )

    response = client.post("/index")

    assert response.status_code == 200
    assert response.json() == {
        "documents": 1,
        "chunks": 1,
    }


def test_index_missing_documents(monkeypatch):
    def fake_load_documents(directory):
        raise NotADirectoryError("Directorio inexistente")

    monkeypatch.setattr(
        main,
        "load_documents",
        fake_load_documents,
    )

    response = client.post("/index")

    assert response.status_code == 404


def test_index_empty_documents(monkeypatch):
    def fake_load_documents(directory):
        raise ValueError("No se encontraron documentos compatibles.")

    monkeypatch.setattr(
        main,
        "load_documents",
        fake_load_documents,
    )

    response = client.post("/index")

    assert response.status_code == 400


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

    monkeypatch.setattr(
        main,
        "get_collection",
        lambda: SimpleNamespace(count=lambda: 1),
    )

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


def test_ask_question_too_long():
    response = client.post(
        "/ask",
        json={
            "question": "a" * 1001,
            "top_k": 4,
        },
    )

    assert response.status_code == 422


def test_ask_without_index(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_collection",
        lambda: SimpleNamespace(count=lambda: 0),
    )

    response = client.post(
        "/ask",
        json={
            "question": "¿Cuántos días de vacaciones?",
            "top_k": 4,
        },
    )

    assert response.status_code == 409
    assert "índice está vacío" in response.json()["detail"]


def test_ask_llm_unavailable(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_collection",
        lambda: SimpleNamespace(count=lambda: 1),
    )

    def fake_ask_question(question, top_k):
        raise APIConnectionError(
            request=httpx.Request(
                "POST",
                "https://api.groq.com/openai/v1/chat/completions",
            )
        )

    monkeypatch.setattr(
        main,
        "ask_question",
        fake_ask_question,
    )

    response = client.post(
        "/ask",
        json={
            "question": "¿Cuántos días de vacaciones?",
            "top_k": 4,
        },
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "No fue posible generar la respuesta con el proveedor LLM."
    }