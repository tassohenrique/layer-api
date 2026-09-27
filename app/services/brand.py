from app.core.exceptions import ConflictError, NotFoundError
from app.models import Brand
from app.repositories.brand import BrandRepository
from app.schemas.brand import BrandCreate, BrandUpdate


class BrandService:
    def __init__(self, repository: BrandRepository) -> None:
        self.repository = repository

    def list_brands(self, skip: int, limit: int) -> list[Brand]:
        return self.repository.list_all(skip, limit)

    def get_brand(self, brand_id: int) -> Brand:
        brand = self.repository.get(brand_id)
        if brand is None:
            raise NotFoundError(f"Brand {brand_id} not found")
        return brand

    def create_brand(self, data: BrandCreate) -> Brand:
        if self.repository.get_by_name(data.name):
            raise ConflictError(f"Brand '{data.name}' already exists")
        return self.repository.create(data)

    def update_brand(self, brand_id: int, data: BrandUpdate) -> Brand:
        brand = self.get_brand(brand_id)

        name_changed = data.name is not None and data.name.lower() != brand.name.lower()
        if name_changed and self.repository.get_by_name(data.name):
            raise ConflictError(f"Brand '{data.name}' already exists")

        return self.repository.update(brand, data)

    def delete_brand(self, brand_id: int) -> None:
        brand = self.get_brand(brand_id)
        self.repository.delete(brand)
