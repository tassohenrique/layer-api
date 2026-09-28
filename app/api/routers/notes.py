from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.note import NoteRepository
from app.schemas.note import NoteCreate, NoteRead, NoteUpdate
from app.services.note import NoteService

router = APIRouter(prefix="/notes", tags=["notes"])


def get_note_service(db: Annotated[Session, Depends(get_db)]) -> NoteService:
    return NoteService(NoteRepository(db))


ServiceDep = Annotated[NoteService, Depends(get_note_service)]


@router.get("", response_model=list[NoteRead])
def list_notes(
    service: ServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Lista as notas olfativas em ordem alfabética, com paginação."""
    return service.list_notes(skip, limit)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, service: ServiceDep):
    """Busca uma nota pelo ID."""
    return service.get_note(note_id)


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(data: NoteCreate, service: ServiceDep):
    """Cadastra uma nova nota olfativa."""
    return service.create_note(data)


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, data: NoteUpdate, service: ServiceDep):
    """Edita uma nota."""
    return service.update_note(note_id, data)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, service: ServiceDep) -> None:
    """Apaga uma nota."""
    service.delete_note(note_id)
