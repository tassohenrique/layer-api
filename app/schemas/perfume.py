from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import Concentration, Gender, NoteLayer


class PerfumeNoteIn(BaseModel):
    """Uma nota informada no cadastro do perfume, com sua camada."""

    note_id: int
    layer: NoteLayer


def ensure_unique_notes(
    notes: list[PerfumeNoteIn] | None,
) -> list[PerfumeNoteIn] | None:
    if notes is None:
        return notes
    note_ids = [note.note_id for note in notes]
    if len(note_ids) != len(set(note_ids)):
        raise ValueError("Each note can appear only once per perfume")
    return notes


class PerfumeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    brand_id: int
    release_year: int | None = Field(default=None, ge=1700, le=2100)
    gender: Gender
    concentration: Concentration | None = None
    perfumer: str | None = Field(default=None, max_length=100)
    notes: list[PerfumeNoteIn] = Field(default_factory=list)

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, notes):
        return ensure_unique_notes(notes)


class PerfumeUpdate(BaseModel):
    """Todos os campos são opcionais. Se 'notes' for enviado, substitui a lista inteira."""

    name: str | None = Field(default=None, min_length=1, max_length=150)
    brand_id: int | None = None
    release_year: int | None = Field(default=None, ge=1700, le=2100)
    gender: Gender | None = None
    concentration: Concentration | None = None
    perfumer: str | None = Field(default=None, max_length=100)
    notes: list[PerfumeNoteIn] | None = None

    @field_validator("name", "brand_id", "gender")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class BrandSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class NoteSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class PerfumeNoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    layer: NoteLayer
    note: NoteSummary


class PerfumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    release_year: int | None
    gender: Gender
    concentration: Concentration | None
    perfumer: str | None
    created_at: datetime
    brand: BrandSummary
    notes: list[PerfumeNoteRead]
