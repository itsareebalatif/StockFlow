import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.inventory import Inventory
from app.models.user import User
from app.models.enums import PurchaseOrderStatus
from app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderStatusUpdate
from app.services.inventory_service import lock_inventory_for_product


def create_purchase_order(
    db: Session, business_user: User, data: PurchaseOrderCreate
) -> PurchaseOrder:
    if not db.query(Supplier).filter(Supplier.id == data.supplier_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

    items: list[PurchaseOrderItem] = []
    total_amount = 0.0
    for item in data.items:
        if not db.query(Product).filter(Product.id == item.product_id).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found",
            )
        total_amount += item.unit_cost * item.quantity
        items.append(
            PurchaseOrderItem(
                product_id=item.product_id, quantity=item.quantity, unit_cost=item.unit_cost
            )
        )

    purchase_order = PurchaseOrder(
        supplier_id=data.supplier_id,
        business_user_id=business_user.id,
        status=PurchaseOrderStatus.DRAFT,
        total_amount=total_amount,
        items=items,
    )
    db.add(purchase_order)
    db.commit()
    db.refresh(purchase_order)
    return purchase_order


def get_purchase_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status_filter: PurchaseOrderStatus | None = None,
) -> list[PurchaseOrder]:
    query = db.query(PurchaseOrder).options(joinedload(PurchaseOrder.items))
    if status_filter is not None:
        query = query.filter(PurchaseOrder.status == status_filter)
    return query.offset(skip).limit(limit).all()


def get_purchase_order_by_id(db: Session, purchase_order_id: uuid.UUID) -> PurchaseOrder:
    purchase_order = (
        db.query(PurchaseOrder)
        .options(joinedload(PurchaseOrder.items))
        .filter(PurchaseOrder.id == purchase_order_id)
        .first()
    )
    if not purchase_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found"
        )
    return purchase_order


def update_purchase_order_status(
    db: Session, purchase_order_id: uuid.UUID, data: PurchaseOrderStatusUpdate
) -> PurchaseOrder:
    purchase_order = (
        db.query(PurchaseOrder)
        .options(joinedload(PurchaseOrder.items))
        .filter(PurchaseOrder.id == purchase_order_id)
        .first()
    )
    if not purchase_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found"
        )

    if (
        data.status == PurchaseOrderStatus.RECEIVED
        and purchase_order.status != PurchaseOrderStatus.RECEIVED
    ):
        for item in purchase_order.items:
            inventory = lock_inventory_for_product(db, item.product_id)
            if inventory:
                inventory.quantity += item.quantity
            else:
                db.add(Inventory(product_id=item.product_id, quantity=item.quantity))

    purchase_order.status = data.status
    db.commit()
    db.refresh(purchase_order)
    return purchase_order
