from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BrandBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    country: str | None = Field(default=None, max_length=60)


class BrandCreate(BrandBase):
    """Dados para cadastrar uma marca."""


class BrandUpdate(BaseModel):
    """Dados para editar uma marca. Todos os campos são opcionais."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    country: str | None = Field(default=None, max_length=60)

    @field_validator("name")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class BrandRead(BrandBase):
    """Dados de uma marca devolvidos pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
