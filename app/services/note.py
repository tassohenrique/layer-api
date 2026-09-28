from app.core.exceptions import ConflictError, NotFoundError
from app.models import Note
from app.repositories.note import NoteRepository
from app.schemas.note import NoteCreate, NoteUpdate


class NoteService:
    def __init__(self, repository: NoteRepository) -> None:
        self.repository = repository

    def list_notes(self, skip: int, limit: int) -> list[Note]:
        return self.repository.list_all(skip, limit)

    def get_note(self, note_id: int) -> Note:
        note = self.repository.get(note_id)
        if note is None:
            raise NotFoundError(f"Note {note_id} not found")
        return note

    def create_note(self, data: NoteCreate) -> Note:
        if self.repository.get_by_name(data.name):
            raise ConflictError(f"Note '{data.name}' already exists")
        return self.repository.create(data)

    def update_note(self, note_id: int, data: NoteUpdate) -> Note:
        note = self.get_note(note_id)

        name_changed = data.name is not None and data.name.lower() != note.name.lower()
        if name_changed and self.repository.get_by_name(data.name):
            raise ConflictError(f"Note '{data.name}' already exists")

        return self.repository.update(note, data)

    def delete_note(self, note_id: int) -> None:
        note = self.get_note(note_id)
        if self.repository.is_in_use(note.id):
            raise ConflictError(
                f"Note {note_id} is used by perfumes and cannot be deleted"
            )
        self.repository.delete(note)
