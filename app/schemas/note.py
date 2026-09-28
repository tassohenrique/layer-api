from datetime import datetime

from pydantic import (  # ← acrescentado field_validator
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class NoteCreate(BaseModel):
    """Dados para cadastrar uma nota olfativa."""

    name: str = Field(min_length=1, max_length=60)


class NoteUpdate(BaseModel):
    """Dados para editar uma nota. O campo é opcional."""

    name: str | None = Field(default=None, min_length=1, max_length=60)

    @field_validator("name")  # ← validador acrescentado
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class NoteRead(BaseModel):
    """Dados de uma nota devolvidos pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
