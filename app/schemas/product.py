import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import ProductStatus


class ProductCreate(BaseModel):
    name: str
    sku: str
    description: str | None = None
    price: float = Field(gt=0)
    category_id: uuid.UUID | None = None
    initial_quantity: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    category_id: uuid.UUID | None = None
    status: ProductStatus | None = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    sku: str
    description: str | None = None
    price: float
    status: ProductStatus
    category_id: uuid.UUID | None = None
    available_quantity: int = 0
