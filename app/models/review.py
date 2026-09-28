from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint(
            "author_id", "perfume_id", name="uq_reviews_author_id_perfume_id"
        ),
        CheckConstraint("rating BETWEEN 1 AND 10", name="ck_reviews_rating_range"),
        CheckConstraint("longevity BETWEEN 1 AND 5", name="ck_reviews_longevity_range"),
        CheckConstraint("sillage BETWEEN 1 AND 5", name="ck_reviews_sillage_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    perfume_id: Mapped[int] = mapped_column(
        ForeignKey("perfumes.id", ondelete="CASCADE"), index=True
    )
    rating: Mapped[int]
    longevity: Mapped[int | None]
    sillage: Mapped[int | None]
    text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    author: Mapped["User"] = relationship()
