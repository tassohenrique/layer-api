from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.repositories.brand import BrandRepository
from app.schemas.brand import BrandCreate, BrandRead, BrandUpdate
from app.services.brand import BrandService

router = APIRouter(prefix="/brands", tags=["brands"])


def get_brand_service(db: Annotated[Session, Depends(get_db)]) -> BrandService:
    return BrandService(BrandRepository(db))


ServiceDep = Annotated[BrandService, Depends(get_brand_service)]


@router.get("", response_model=list[BrandRead])
def list_brands(
    service: ServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Lista as marcas em ordem alfabética, com paginação."""
    return service.list_brands(skip, limit)


@router.get("/{brand_id}", response_model=BrandRead)
def get_brand(brand_id: int, service: ServiceDep):
    """Busca uma marca pelo ID."""
    return service.get_brand(brand_id)


@router.post(
    "",
    response_model=BrandRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_brand(data: BrandCreate, service: ServiceDep):
    """Cadastra uma nova marca. Requer administrador."""
    return service.create_brand(data)


@router.patch(
    "/{brand_id}", response_model=BrandRead, dependencies=[Depends(require_admin)]
)
def update_brand(brand_id: int, data: BrandUpdate, service: ServiceDep):
    """Edita uma marca. Só os campos enviados são alterados. Requer administrador."""
    return service.update_brand(brand_id, data)


@router.delete(
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_brand(brand_id: int, service: ServiceDep) -> None:
    """Apaga uma marca. Requer administrador."""
    service.delete_brand(brand_id)
