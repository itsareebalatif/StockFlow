import enum


class UserRole(str, enum.Enum):
    BUSINESS = "BUSINESS"
    CUSTOMER = "CUSTOMER"


class ProductStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    FULFILLED = "FULFILLED"


class PurchaseOrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ORDERED = "ORDERED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"