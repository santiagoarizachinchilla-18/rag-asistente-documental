from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf"}


def load_document(file_path: Path) -> dict:
    """Extrae el texto y conserva el nombre del documento."""

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"No existe el archivo: {file_path}"
        )

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Formato no soportado: {extension}"
        )

    if extension == ".pdf":
        reader = PdfReader(str(file_path))

        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )
    else:
        text = file_path.read_text(encoding="utf-8")

    if not text.strip():
        raise ValueError(
            f"El documento no contiene texto: {file_path.name}"
        )

    return {
        "source": file_path.name,
        "text": text,
    }


def load_documents(directory: Path) -> list[dict]:
    """Carga los documentos compatibles de una carpeta."""

    directory = Path(directory)

    if not directory.is_dir():
        raise NotADirectoryError(
            f"No existe el directorio: {directory}"
        )

    documents = []

    for file_path in sorted(directory.iterdir()):
        if (
            file_path.is_file()
            and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
        ):
            documents.append(load_document(file_path))

    if not documents:
        raise ValueError(
            "No se encontraron documentos compatibles."
        )

    return documents