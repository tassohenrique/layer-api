from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.models import Note, PerfumeNote
from app.schemas.note import NoteCreate, NoteUpdate


class NoteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self, skip: int, limit: int) -> list[Note]:
        stmt = select(Note).order_by(Note.name).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def get(self, note_id: int) -> Note | None:
        return self.db.get(Note, note_id)

    def get_by_name(self, name: str) -> Note | None:
        stmt = select(Note).where(func.lower(Note.name) == name.lower())
        return self.db.scalar(stmt)

    def get_many(self, note_ids: set[int]) -> list[Note]:
        stmt = select(Note).where(Note.id.in_(note_ids))
        return list(self.db.scalars(stmt))

    def is_in_use(self, note_id: int) -> bool:
        stmt = select(exists().where(PerfumeNote.note_id == note_id))
        return bool(self.db.scalar(stmt))

    def create(self, data: NoteCreate) -> Note:
        note = Note(**data.model_dump())
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def update(self, note: Note, data: NoteUpdate) -> Note:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(note, field, value)
        self.db.commit()
        self.db.refresh(note)
        return note

    def delete(self, note: Note) -> None:
        self.db.delete(note)
        self.db.commit()
