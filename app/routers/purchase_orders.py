import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderOut,
    PurchaseOrderStatusUpdate,
)
from app.models.enums import PurchaseOrderStatus
from app.services import purchase_order_service
from app.dependencies.auth import require_business
from app.models.user import User

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


@router.post("", response_model=PurchaseOrderOut, status_code=status.HTTP_201_CREATED)
def create_purchase_order(
    payload: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
):
    return purchase_order_service.create_purchase_order(db, current_user, payload)


@router.get("", response_model=list[PurchaseOrderOut])
def list_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    status_filter: PurchaseOrderStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
):
    return purchase_order_service.get_purchase_orders(db, skip, limit, status_filter)


@router.get("/{purchase_order_id}", response_model=PurchaseOrderOut)
def get_purchase_order(
    purchase_order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
):
    return purchase_order_service.get_purchase_order_by_id(db, purchase_order_id)


@router.patch("/{purchase_order_id}/status", response_model=PurchaseOrderOut)
def update_purchase_order_status(
    purchase_order_id: uuid.UUID,
    payload: PurchaseOrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
):
    return purchase_order_service.update_purchase_order_status(db, purchase_order_id, payload)
