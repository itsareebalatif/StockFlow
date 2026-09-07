import uuid
from pydantic import BaseModel, ConfigDict, Field


class InventoryUpdate(BaseModel):
    quantity: int = Field(ge=0)


class InventoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
