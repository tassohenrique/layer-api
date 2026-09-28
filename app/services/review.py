from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models import Review, User, UserRole
from app.repositories.perfume import PerfumeRepository
from app.repositories.review import ReviewRepository
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewService:
    def __init__(self, reviews: ReviewRepository, perfumes: PerfumeRepository) -> None:
        self.reviews = reviews
        self.perfumes = perfumes

    def list_reviews(self, perfume_id: int, skip: int, limit: int) -> list[Review]:
        self._ensure_perfume_exists(perfume_id)
        return self.reviews.list_for_perfume(perfume_id, skip, limit)

    def create_review(
        self, perfume_id: int, author: User, data: ReviewCreate
    ) -> Review:
        self._ensure_perfume_exists(perfume_id)

        if self.reviews.get_by_author_and_perfume(author.id, perfume_id):
            raise ConflictError("You have already reviewed this perfume")

        review = Review(**data.model_dump(), perfume_id=perfume_id, author_id=author.id)
        return self.reviews.create(review)

    def update_review(self, review_id: int, user: User, data: ReviewUpdate) -> Review:
        review = self._get_review(review_id)

        if review.author_id != user.id:
            raise ForbiddenError("You can only edit your own reviews")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(review, field, value)
        return self.reviews.save(review)

    def delete_review(self, review_id: int, user: User) -> None:
        review = self._get_review(review_id)

        is_author = review.author_id == user.id
        is_admin = user.role == UserRole.ADMIN
        if not (is_author or is_admin):
            raise ForbiddenError("You can only delete your own reviews")

        self.reviews.delete(review)

    def _get_review(self, review_id: int) -> Review:
        review = self.reviews.get(review_id)
        if review is None:
            raise NotFoundError(f"Review {review_id} not found")
        return review

    def _ensure_perfume_exists(self, perfume_id: int) -> None:
        if self.perfumes.get(perfume_id) is None:
            raise NotFoundError(f"Perfume {perfume_id} not found")
