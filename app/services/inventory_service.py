import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryUpdate


def lock_inventory_for_product(db: Session, product_id: uuid.UUID) -> Inventory | None:

    return (
        db.query(Inventory)
        .filter(Inventory.product_id == product_id)
        .with_for_update()
        .first()
    )


def get_inventories(db: Session, skip: int = 0, limit: int = 100) -> list[Inventory]:
    return db.query(Inventory).offset(skip).limit(limit).all()


def get_inventory_by_product(db: Session, product_id: uuid.UUID) -> Inventory:
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Inventory record not found"
        )
    return inventory


def update_inventory_quantity(
    db: Session, product_id: uuid.UUID, data: InventoryUpdate
) -> Inventory:
    inventory = get_inventory_by_product(db, product_id)
    inventory.quantity = data.quantity
    db.commit()
    db.refresh(inventory)
    return inventory
