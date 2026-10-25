import re
from pathlib import Path


def split_text(
    text: str,
    chunk_size: int = 400,
    chunk_overlap: int = 60,
) -> list[str]:
    """Divide texto en fragmentos con solapamiento."""

    if chunk_size <= 0:
        raise ValueError("chunk_size debe ser positivo.")

    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError(
            "chunk_overlap debe ser menor que chunk_size."
        )

    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            sentence_boundary = text.rfind(
                ". ",
                start + chunk_size // 2,
                end,
            )

            if sentence_boundary != -1:
                end = sentence_boundary + 1
            else:
                separator = text.rfind(" ", start, end)

                if separator > start:
                    end = separator

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        next_start = end - chunk_overlap

        if chunk_overlap > 0:
            sentence_boundary = text.rfind(
                ". ",
                start,
                next_start,
            )

            if sentence_boundary != -1:
                next_start = sentence_boundary + 2
            else:
                word_boundary = text.rfind(
                    " ",
                    start,
                    next_start,
                )

                if word_boundary != -1:
                    next_start = word_boundary + 1

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 400,
    chunk_overlap: int = 60,
) -> list[dict]:
    """Fragmenta documentos conservando metadatos."""

    results = []

    for document in documents:
        source = document["source"]
        text = document["text"]

        chunks = split_text(
            text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        source_id = Path(source).stem

        for index, chunk in enumerate(chunks, start=1):
            results.append(
                {
                    "chunk_id": f"{source_id}_{index:03d}",
                    "source": source,
                    "text": chunk,
                }
            )

    return results