from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from app.db.base import Base
from app.models.enums import Concentration, Gender, NoteLayer
from app.models.review import Review

if TYPE_CHECKING:
    from app.models.brand import Brand
    from app.models.note import Note


def enum_column(enum_class):
    """Guarda o enum como texto (ex: 'edp'), sem criar um tipo especial no Postgres."""
    return Enum(
        enum_class,
        native_enum=False,
        length=20,
        values_callable=lambda members: [member.value for member in members],
    )


class Perfume(Base):
    __tablename__ = "perfumes"
    __table_args__ = (
        UniqueConstraint("brand_id", "name", name="uq_perfumes_brand_id_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    brand_id: Mapped[int] = mapped_column(
        ForeignKey("brands.id", ondelete="RESTRICT"), index=True
    )
    release_year: Mapped[int | None]
    gender: Mapped[Gender] = mapped_column(enum_column(Gender))
    concentration: Mapped[Concentration | None] = mapped_column(
        enum_column(Concentration)
    )
    perfumer: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    average_rating: Mapped[float | None] = column_property(
        select(func.round(func.avg(Review.rating), 1))
        .where(Review.perfume_id == id)
        .correlate_except(Review)
        .scalar_subquery()
    )
    review_count: Mapped[int] = column_property(
        select(func.count(Review.id))
        .where(Review.perfume_id == id)
        .correlate_except(Review)
        .scalar_subquery()
    )

    brand: Mapped["Brand"] = relationship(back_populates="perfumes")
    notes: Mapped[list["PerfumeNote"]] = relationship(
        back_populates="perfume", cascade="all, delete-orphan"
    )


class PerfumeNote(Base):
    """Liga um perfume a uma nota, informando em qual camada ela aparece."""

    __tablename__ = "perfume_notes"

    perfume_id: Mapped[int] = mapped_column(
        ForeignKey("perfumes.id", ondelete="CASCADE"), primary_key=True
    )
    note_id: Mapped[int] = mapped_column(
        ForeignKey("notes.id", ondelete="RESTRICT"), primary_key=True
    )
    layer: Mapped[NoteLayer] = mapped_column(enum_column(NoteLayer))

    perfume: Mapped[Perfume] = relationship(back_populates="notes")
    note: Mapped["Note"] = relationship()
