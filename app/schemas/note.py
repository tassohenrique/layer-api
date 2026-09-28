from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    """Dados para cadastrar uma nota olfativa."""

    name: str = Field(min_length=1, max_length=60)


class NoteUpdate(BaseModel):
    """Dados para editar uma nota. O campo é opcional."""

    name: str | None = Field(default=None, min_length=1, max_length=60)


class NoteRead(BaseModel):
    """Dados de uma nota devolvidos pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
