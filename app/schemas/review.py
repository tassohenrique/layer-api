from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=10)
    longevity: int | None = Field(default=None, ge=1, le=5)
    sillage: int | None = Field(default=None, ge=1, le=5)
    text: str | None = Field(default=None, max_length=2000)


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=10)
    longevity: int | None = Field(default=None, ge=1, le=5)
    sillage: int | None = Field(default=None, ge=1, le=5)
    text: str | None = Field(default=None, max_length=2000)

    @field_validator("rating")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class ReviewAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    perfume_id: int
    rating: int
    longevity: int | None
    sillage: int | None
    text: str | None
    created_at: datetime
    updated_at: datetime
    author: ReviewAuthor
