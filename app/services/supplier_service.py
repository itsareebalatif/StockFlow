import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


def get_suppliers(db: Session, skip: int = 0, limit: int = 100) -> list[Supplier]:
    return db.query(Supplier).offset(skip).limit(limit).all()


def get_supplier_by_id(db: Session, supplier_id: uuid.UUID) -> Supplier:
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier


def create_supplier(db: Session, data: SupplierCreate) -> Supplier:
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def update_supplier(db: Session, supplier_id: uuid.UUID, data: SupplierUpdate) -> Supplier:
    supplier = get_supplier_by_id(db, supplier_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)
    db.commit()
    db.refresh(supplier)
    return supplier


def delete_supplier(db: Session, supplier_id: uuid.UUID) -> None:
    supplier = get_supplier_by_id(db, supplier_id)
    db.delete(supplier)
    db.commit()
