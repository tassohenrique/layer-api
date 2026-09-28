from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.db.session import get_db
from app.repositories.perfume import PerfumeRepository
from app.repositories.review import ReviewRepository
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.services.review import ReviewService

router = APIRouter(tags=["reviews"])


def get_review_service(db: Annotated[Session, Depends(get_db)]) -> ReviewService:
    return ReviewService(ReviewRepository(db), PerfumeRepository(db))


ServiceDep = Annotated[ReviewService, Depends(get_review_service)]


@router.get("/perfumes/{perfume_id}/reviews", response_model=list[ReviewRead])
def list_reviews(
    perfume_id: int,
    service: ServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Lista as reviews de um perfume, das mais recentes para as mais antigas."""
    return service.list_reviews(perfume_id, skip, limit)


@router.post(
    "/perfumes/{perfume_id}/reviews",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    perfume_id: int, data: ReviewCreate, current_user: CurrentUser, service: ServiceDep
):
    """Avalia um perfume. Requer login. Cada usuário avalia cada perfume uma vez."""
    return service.create_review(perfume_id, current_user, data)


@router.patch("/reviews/{review_id}", response_model=ReviewRead)
def update_review(
    review_id: int, data: ReviewUpdate, current_user: CurrentUser, service: ServiceDep
):
    """Edita uma review. Só o autor pode editar."""
    return service.update_review(review_id, current_user, data)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int, current_user: CurrentUser, service: ServiceDep
) -> None:
    """Apaga uma review. O autor pode apagar a sua, e o admin pode apagar qualquer uma."""
    service.delete_review(review_id, current_user)
