from app.core.exceptions import ConflictError, NotFoundError
from app.models import Perfume, PerfumeNote
from app.repositories.brand import BrandRepository
from app.repositories.note import NoteRepository
from app.repositories.perfume import PerfumeRepository
from app.schemas.perfume import PerfumeCreate, PerfumeNoteIn, PerfumeUpdate


class PerfumeService:
    def __init__(
        self,
        perfumes: PerfumeRepository,
        brands: BrandRepository,
        notes: NoteRepository,
    ) -> None:
        self.perfumes = perfumes
        self.brands = brands
        self.notes = notes

    def list_perfumes(
        self, skip: int, limit: int, brand_id: int | None = None
    ) -> list[Perfume]:
        return self.perfumes.list_all(skip, limit, brand_id)

    def get_perfume(self, perfume_id: int) -> Perfume:
        perfume = self.perfumes.get(perfume_id)
        if perfume is None:
            raise NotFoundError(f"Perfume {perfume_id} not found")
        return perfume

    def create_perfume(self, data: PerfumeCreate) -> Perfume:
        self._ensure_brand_exists(data.brand_id)
        self._ensure_name_available(data.brand_id, data.name)

        perfume = Perfume(
            **data.model_dump(exclude={"notes"}),
            notes=self._build_notes(data.notes),
        )
        return self.perfumes.create(perfume)

    def update_perfume(self, perfume_id: int, data: PerfumeUpdate) -> Perfume:
        perfume = self.get_perfume(perfume_id)
        changes = data.model_dump(exclude_unset=True, exclude={"notes"})

        new_brand_id = changes.get("brand_id", perfume.brand_id)
        new_name = changes.get("name", perfume.name)

        if new_brand_id != perfume.brand_id:
            self._ensure_brand_exists(new_brand_id)

        identity_changed = (
            new_brand_id != perfume.brand_id or new_name.lower() != perfume.name.lower()
        )
        if identity_changed:
            self._ensure_name_available(new_brand_id, new_name)

        for field, value in changes.items():
            setattr(perfume, field, value)

        if data.notes is not None:
            self.perfumes.replace_notes(perfume, self._build_notes(data.notes))

        return self.perfumes.save(perfume)

    def delete_perfume(self, perfume_id: int) -> None:
        perfume = self.get_perfume(perfume_id)
        self.perfumes.delete(perfume)

    def _ensure_brand_exists(self, brand_id: int) -> None:
        if self.brands.get(brand_id) is None:
            raise NotFoundError(f"Brand {brand_id} not found")

    def _ensure_name_available(self, brand_id: int, name: str) -> None:
        if self.perfumes.get_by_brand_and_name(brand_id, name):
            raise ConflictError(f"Perfume '{name}' already exists for this brand")

    def _build_notes(self, notes_in: list[PerfumeNoteIn]) -> list[PerfumeNote]:
        if not notes_in:
            return []

        requested_ids = {note.note_id for note in notes_in}
        found_ids = {note.id for note in self.notes.get_many(requested_ids)}
        missing_ids = requested_ids - found_ids
        if missing_ids:
            raise NotFoundError(f"Notes not found: {sorted(missing_ids)}")

        return [
            PerfumeNote(note_id=note.note_id, layer=note.layer) for note in notes_in
        ]
