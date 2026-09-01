import uuid
from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str
    description: str | None = None

class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class CategoryOut(BaseModel):
    id: uuid.UUID
    name: str
    description : str | None = None

    class config:
        from_attribute = True
                