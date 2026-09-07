import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User
from app.models.enums import OrderStatus, ProductStatus, UserRole
from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.services.inventory_service import lock_inventory_for_product


def create_order(db: Session, customer: User, data: OrderCreate) -> Order:
    order_items: list[OrderItem] = []
    total_amount = 0.0

    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or product.status != ProductStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not available",
            )

        inventory = lock_inventory_for_product(db, product.id)
        if not inventory or inventory.quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product.name}",
            )

        inventory.quantity -= item.quantity
        unit_price = float(product.price)
        total_amount += unit_price * item.quantity
        order_items.append(
            OrderItem(product_id=product.id, quantity=item.quantity, unit_price=unit_price)
        )

    order = Order(
        customer_id=customer.id,
        status=OrderStatus.PENDING,
        total_amount=total_amount,
        items=order_items,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_orders(
    db: Session, user: User, skip: int = 0, limit: int = 100, status_filter: OrderStatus | None = None
) -> list[Order]:
    query = db.query(Order).options(joinedload(Order.items))
    if user.role == UserRole.CUSTOMER:
        query = query.filter(Order.customer_id == user.id)
    if status_filter is not None:
        query = query.filter(Order.status == status_filter)
    return query.offset(skip).limit(limit).all()


def get_order_by_id(db: Session, user: User, order_id: uuid.UUID) -> Order:
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )
    if not order or (user.role == UserRole.CUSTOMER and order.customer_id != user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


def update_order_status(db: Session, order_id: uuid.UUID, data: OrderStatusUpdate) -> Order:
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    restockable = order.status not in (OrderStatus.CANCELLED, OrderStatus.FULFILLED)
    if data.status == OrderStatus.CANCELLED and restockable:
        for item in order.items:
            inventory = lock_inventory_for_product(db, item.product_id)
            if inventory:
                inventory.quantity += item.quantity

    order.status = data.status
    db.commit()
    db.refresh(order)
    return order
