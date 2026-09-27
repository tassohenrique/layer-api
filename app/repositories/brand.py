from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Brand
from app.schemas.brand import BrandCreate, BrandUpdate


class BrandRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self, skip: int, limit: int) -> list[Brand]:
        stmt = select(Brand).order_by(Brand.name).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def get(self, brand_id: int) -> Brand | None:
        return self.db.get(Brand, brand_id)

    def get_by_name(self, name: str) -> Brand | None:
        stmt = select(Brand).where(func.lower(Brand.name) == name.lower())
        return self.db.scalar(stmt)

    def create(self, data: BrandCreate) -> Brand:
        brand = Brand(**data.model_dump())
        self.db.add(brand)
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def update(self, brand: Brand, data: BrandUpdate) -> Brand:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(brand, field, value)
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def delete(self, brand: Brand) -> None:
        self.db.delete(brand)
        self.db.commit()
