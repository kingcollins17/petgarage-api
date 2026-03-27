from enum import Enum
from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel


class PaymentMethod(str, Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    USSD = "ussd"
    CASH = "cash"


class PaymentProvider(str, Enum):
    PAYSTACK = "paystack"
    FLUTTERWAVE = "flutterwave"
    CASH_ON_DELIVERY = "cod"
    MANUAL = "manual"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)

    # Strategy Fields
    provider: PaymentProvider = Field(default=PaymentProvider.PAYSTACK)
    method: PaymentMethod = Field(default=PaymentMethod.CARD)

    # Reference Handling
    # For COD, this could be a generated Receipt ID
    external_reference: str = Field(unique=True, index=True)

    amount: float
    currency: str = Field(default="NGN")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)

    # Metadata (Stores raw JSON from Paystack/Flutterwave for debugging)
    provider_metadata: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None  # When the money actually hit your account

    order: "Order" = Relationship(back_populates="payments")
