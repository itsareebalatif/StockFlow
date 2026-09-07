import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.enums import ProductStatus
from app.schemas.product import ProductCreate, ProductUpdate


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category_id: uuid.UUID | None = None,
    active_only: bool = False,
) -> list[Product]:
    query = db.query(Product).options(joinedload(Product.inventory))
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if active_only:
        query = query.filter(Product.status == ProductStatus.ACTIVE)
    return query.offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: uuid.UUID) -> Product:
    product = (
        db.query(Product)
        .options(joinedload(Product.inventory))
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def create_product(db: Session, data: ProductCreate) -> Product:
    if db.query(Product).filter(Product.sku == data.sku).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="SKU already exists"
        )

    product = Product(
        name=data.name,
        sku=data.sku,
        description=data.description,
        price=data.price,
        category_id=data.category_id,
    )
    db.add(product)
    db.flush()

    inventory = Inventory(product_id=product.id, quantity=data.initial_quantity)
    db.add(inventory)

    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: uuid.UUID, data: ProductUpdate) -> Product:
    product = get_product_by_id(db, product_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: uuid.UUID) -> None:
    product = get_product_by_id(db, product_id)
    db.delete(product)
    db.commit()
