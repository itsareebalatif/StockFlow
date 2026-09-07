import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.inventory import InventoryUpdate, InventoryOut
from app.services import inventory_service
from app.dependencies.auth import require_business
from app.models.user import User

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=list[InventoryOut])
def list_inventory(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
):
    return inventory_service.get_inventories(db, skip, limit)


@router.get("/{product_id}", response_model=InventoryOut)
def get_inventory(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
):
    return inventory_service.get_inventory_by_product(db, product_id)


@router.patch("/{product_id}", response_model=InventoryOut)
def update_inventory(
    product_id: uuid.UUID,
    payload: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
):
    return inventory_service.update_inventory_quantity(db, product_id, payload)
