import pytest

from app.chunker import chunk_documents, split_text


def test_short_text():
    chunks = split_text("Texto pequeño")

    assert chunks == ["Texto pequeño"]


def test_empty_text():
    assert split_text("   ") == []


def test_invalid_parameters():
    with pytest.raises(ValueError):
        split_text("Texto", chunk_size=100, chunk_overlap=100)


def test_chunk_size():
    text = "Esta es una oración de prueba. " * 30

    chunks = split_text(
        text,
        chunk_size=100,
        chunk_overlap=20,
    )

    assert len(chunks) > 1
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_chunk_metadata():
    documents = [
        {
            "source": "politica_vacaciones.md",
            "text": "Los empleados tienen 15 días hábiles.",
        }
    ]

    chunks = chunk_documents(documents)

    assert len(chunks) == 1
    assert chunks[0]["chunk_id"] == "politica_vacaciones_001"
    assert chunks[0]["source"] == "politica_vacaciones.md"