import pytest

from app import vector_store


@pytest.fixture
def temporary_store(tmp_path, monkeypatch):
    monkeypatch.setattr(
        vector_store,
        "CHROMA_PATH",
        tmp_path / "chroma",
    )
    monkeypatch.setattr(
        vector_store,
        "COLLECTION_NAME",
        "coleccion_pruebas",
    )


def make_chunk(chunk_id, text):
    return {
        "chunk_id": chunk_id,
        "source": "documento_prueba.md",
        "text": text,
    }


def test_index_chunks(temporary_store):
    chunks = [
        make_chunk("chunk_001", "Vacaciones"),
        make_chunk("chunk_002", "Trabajo remoto"),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    count = vector_store.index_chunks(
        chunks,
        embeddings,
    )

    assert count == 2
    assert vector_store.get_collection().count() == 2


def test_search_similar(temporary_store):
    chunks = [
        make_chunk("chunk_001", "Vacaciones"),
        make_chunk("chunk_002", "Trabajo remoto"),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    vector_store.index_chunks(chunks, embeddings)

    results = vector_store.search_similar(
        [1.0, 0.0, 0.0],
        top_k=2,
    )

    assert len(results) == 2
    assert results[0]["chunk_id"] == "chunk_001"
    assert results[0]["source"] == "documento_prueba.md"
    assert results[0]["distance"] <= results[1]["distance"]


def test_reindex_replaces_old_chunks(temporary_store):
    vector_store.index_chunks(
        [make_chunk("antiguo_001", "Contenido antiguo")],
        [[1.0, 0.0, 0.0]],
    )

    count = vector_store.index_chunks(
        [make_chunk("nuevo_001", "Contenido nuevo")],
        [[0.0, 1.0, 0.0]],
    )

    assert count == 1

    stored = vector_store.get_collection().get()

    assert stored["ids"] == ["nuevo_001"]
    assert "antiguo_001" not in stored["ids"]


def test_mismatched_embeddings(temporary_store):
    chunks = [
        make_chunk("chunk_001", "Texto de prueba")
    ]

    with pytest.raises(ValueError):
        vector_store.index_chunks(chunks, [])


def test_empty_index(temporary_store):
    with pytest.raises(ValueError):
        vector_store.index_chunks([], [])