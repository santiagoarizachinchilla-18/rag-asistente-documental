from pathlib import Path

import chromadb


CHROMA_PATH = Path("data/chroma")
COLLECTION_NAME = "politicas_internas"


def get_client():
    """Inicializa el almacenamiento persistente."""

    CHROMA_PATH.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )


def get_collection():
    """Obtiene o crea la colección vectorial."""

    client = get_client()

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        configuration={
            "hnsw": {
                "space": "cosine"
            }
        },
    )


def index_chunks(chunks: list[dict], embeddings: list[list[float]]) -> int:
    """Reemplaza el índice con los fragmentos recibidos."""

    if not chunks:
        raise ValueError("No hay fragmentos para indexar.")

    if len(chunks) != len(embeddings):
        raise ValueError(
            "La cantidad de fragmentos y embeddings no coincide."
        )

    client = get_client()

    # Reindexación completa para evitar fragmentos obsoletos.
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except chromadb.errors.NotFoundError:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        configuration={
            "hnsw": {
                "space": "cosine"
            }
        },
    )

    collection.add(
        ids=[chunk["chunk_id"] for chunk in chunks],
        documents=[chunk["text"] for chunk in chunks],
        metadatas=[
            {"source": chunk["source"]}
            for chunk in chunks
        ],
        embeddings=embeddings,
    )

    return collection.count()


def search_similar(
    query_embedding: list[float],
    top_k: int = 4,
) -> list[dict]:
    """Recupera los fragmentos vectorialmente más cercanos."""

    collection = get_collection()

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    matches = []

    for chunk_id, text, metadata, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        matches.append(
            {
                "chunk_id": chunk_id,
                "source": metadata["source"],
                "text": text,
                "distance": float(distance),
            }
        )

    return matches