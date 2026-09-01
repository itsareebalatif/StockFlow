import uuid
from sqlalchemy import String,Boolean,Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.enums import UserRole

class User(Base):
    __tablename__="users"
    id: Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4   
    )

    email:Mapped[str]= mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password:Mapped[str]= mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole),default=UserRole.CUSTOMER, nullable=False)
    #is_active: Mapped[bool] = mapped_column(Boolean, default=True)



    orders = relationship("Order", back_populates="customer")
    purchase_orders = relationship("PurchaseOrder", back_populates="business_user")

