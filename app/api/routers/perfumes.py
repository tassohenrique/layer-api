from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.brand import BrandRepository
from app.repositories.note import NoteRepository
from app.repositories.perfume import PerfumeRepository
from app.schemas.perfume import PerfumeCreate, PerfumeRead, PerfumeUpdate
from app.services.perfume import PerfumeService

router = APIRouter(prefix="/perfumes", tags=["perfumes"])


def get_perfume_service(db: Annotated[Session, Depends(get_db)]) -> PerfumeService:
    return PerfumeService(
        PerfumeRepository(db),
        BrandRepository(db),
        NoteRepository(db),
    )


ServiceDep = Annotated[PerfumeService, Depends(get_perfume_service)]


@router.get("", response_model=list[PerfumeRead])
def list_perfumes(
    service: ServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    brand_id: Annotated[int | None, Query(description="Filtra por marca")] = None,
):
    """Lista os perfumes em ordem alfabética, com paginação e filtro por marca."""
    return service.list_perfumes(skip, limit, brand_id)


@router.get("/{perfume_id}", response_model=PerfumeRead)
def get_perfume(perfume_id: int, service: ServiceDep):
    """Busca um perfume pelo ID, com a marca e as notas."""
    return service.get_perfume(perfume_id)


@router.post("", response_model=PerfumeRead, status_code=status.HTTP_201_CREATED)
def create_perfume(data: PerfumeCreate, service: ServiceDep):
    """Cadastra um perfume, já com suas notas por camada."""
    return service.create_perfume(data)


@router.patch("/{perfume_id}", response_model=PerfumeRead)
def update_perfume(perfume_id: int, data: PerfumeUpdate, service: ServiceDep):
    """Edita um perfume. Se 'notes' for enviado, substitui todas as notas."""
    return service.update_perfume(perfume_id, data)


@router.delete("/{perfume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_perfume(perfume_id: int, service: ServiceDep) -> None:
    """Apaga um perfume e suas ligações com as notas."""
    service.delete_perfume(perfume_id)
