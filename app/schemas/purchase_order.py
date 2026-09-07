import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import PurchaseOrderStatus


class PurchaseOrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(gt=0)
    unit_cost: float = Field(gt=0)


class PurchaseOrderCreate(BaseModel):
    supplier_id: uuid.UUID
    items: list[PurchaseOrderItemCreate] = Field(min_length=1)


class PurchaseOrderStatusUpdate(BaseModel):
    status: PurchaseOrderStatus


class PurchaseOrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_cost: float


class PurchaseOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    supplier_id: uuid.UUID
    business_user_id: uuid.UUID
    status: PurchaseOrderStatus
    total_amount: float
    items: list[PurchaseOrderItemOut] = []
