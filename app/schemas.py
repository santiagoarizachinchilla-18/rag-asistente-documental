from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=4, ge=1)


class SourceReference(BaseModel):
    reference: int
    source: str
    chunk_id: str
    excerpt: str
    distance: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceReference]


class IndexResponse(BaseModel):
    documents: int
    chunks: int