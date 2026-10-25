from pathlib import Path

from fastapi import FastAPI, HTTPException
from openai import APIError

from app.chunker import chunk_documents
from app.document_loader import load_documents
from app.embeddings import generate_embeddings
from app.rag_service import ask_question
from app.schemas import AskRequest, AskResponse, IndexResponse
from app.vector_store import get_collection, index_chunks


app = FastAPI(
    title="RAG - Asistente Documental",
    description="Consulta de documentos internos con respuestas fundamentadas.",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/index", response_model=IndexResponse)
def index_documents():
    try:
        documents = load_documents(Path("documents"))
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el directorio de documentos.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="No se encontraron documentos válidos para indexar.",
        ) from exc

    chunks = chunk_documents(documents)

    embeddings = generate_embeddings(
        [chunk["text"] for chunk in chunks]
    )

    count = index_chunks(chunks, embeddings)

    return {
        "documents": len(documents),
        "chunks": count,
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=422,
            detail="La pregunta no puede estar vacía.",
        )

    if get_collection().count() == 0:
        raise HTTPException(
            status_code=409,
            detail="El índice está vacío. Ejecuta POST /index primero.",
        )

    try:
        return ask_question(
            question=request.question,
            top_k=request.top_k,
        )
    except APIError as exc:
        raise HTTPException(
            status_code=503,
            detail="No fue posible generar la respuesta con el proveedor LLM.",
        ) from exc