from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Perfume, PerfumeNote


class PerfumeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _query_with_relations(self):
        """Consulta base que já traz marca e notas, evitando o problema N+1.

        populate_existing garante que a média e a contagem de reviews venham
        atualizadas, mesmo se o perfume já estiver carregado na sessão.
        """
        return (
            select(Perfume)
            .options(
                selectinload(Perfume.brand),
                selectinload(Perfume.notes).selectinload(PerfumeNote.note),
            )
            .execution_options(populate_existing=True)
        )

    def list_all(
        self,
        skip: int,
        limit: int,
        brand_id: int | None = None,
        sort: str = "name",
    ) -> list[Perfume]:
        stmt = self._query_with_relations()
        if brand_id is not None:
            stmt = stmt.where(Perfume.brand_id == brand_id)

        if sort == "rating":
            stmt = stmt.order_by(
                Perfume.average_rating.desc().nulls_last(), Perfume.name
            )
        else:
            stmt = stmt.order_by(Perfume.name)

        stmt = stmt.offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def get(self, perfume_id: int) -> Perfume | None:
        stmt = self._query_with_relations().where(Perfume.id == perfume_id)
        return self.db.scalar(stmt)

    def get_by_brand_and_name(self, brand_id: int, name: str) -> Perfume | None:
        stmt = select(Perfume).where(
            Perfume.brand_id == brand_id,
            func.lower(Perfume.name) == name.lower(),
        )
        return self.db.scalar(stmt)

    def create(self, perfume: Perfume) -> Perfume:
        self.db.add(perfume)
        self.db.commit()
        self.db.refresh(perfume)
        return perfume

    def save(self, perfume: Perfume) -> Perfume:
        self.db.commit()
        self.db.refresh(perfume)
        return perfume

    def replace_notes(self, perfume: Perfume, notes: list[PerfumeNote]) -> None:
        perfume.notes.clear()
        self.db.flush()
        perfume.notes.extend(notes)

    def delete(self, perfume: Perfume) -> None:
        self.db.delete(perfume)
        self.db.commit()
