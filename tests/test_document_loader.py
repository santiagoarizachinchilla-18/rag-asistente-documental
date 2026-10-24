import pytest

from app.document_loader import load_document, load_documents


def test_load_markdown(tmp_path):
    file_path = tmp_path / "documento.md"
    file_path.write_text("Contenido de prueba", encoding="utf-8")

    result = load_document(file_path)

    assert result["source"] == "documento.md"
    assert result["text"] == "Contenido de prueba"


def test_load_empty_document(tmp_path):
    file_path = tmp_path / "vacio.txt"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError):
        load_document(file_path)


def test_load_documents(tmp_path):
    (tmp_path / "uno.md").write_text("Primero", encoding="utf-8")
    (tmp_path / "dos.txt").write_text("Segundo", encoding="utf-8")

    documents = load_documents(tmp_path)

    assert len(documents) == 2