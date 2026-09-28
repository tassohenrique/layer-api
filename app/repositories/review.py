from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Review


class ReviewRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_perfume(self, perfume_id: int, skip: int, limit: int) -> list[Review]:
        stmt = (
            select(Review)
            .options(selectinload(Review.author))
            .where(Review.perfume_id == perfume_id)
            .order_by(Review.created_at.desc(), Review.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def get(self, review_id: int) -> Review | None:
        return self.db.get(Review, review_id)

    def get_by_author_and_perfume(
        self, author_id: int, perfume_id: int
    ) -> Review | None:
        stmt = select(Review).where(
            Review.author_id == author_id,
            Review.perfume_id == perfume_id,
        )
        return self.db.scalar(stmt)

    def create(self, review: Review) -> Review:
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def save(self, review: Review) -> Review:
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete(self, review: Review) -> None:
        self.db.delete(review)
        self.db.commit()
