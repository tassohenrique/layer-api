from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BrandBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    country: str | None = Field(default=None, max_length=60)


class BrandCreate(BrandBase):
    """Dados para cadastrar uma marca."""


class BrandUpdate(BaseModel):
    """Dados para editar uma marca. Todos os campos são opcionais."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    country: str | None = Field(default=None, max_length=60)


class BrandRead(BrandBase):
    """Dados de uma marca devolvidos pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
