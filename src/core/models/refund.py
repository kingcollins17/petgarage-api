class RefundStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Refund(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    payment_id: int = Field(foreign_key="payment.id", index=True)

    amount: float
    reason: str
    status: RefundStatus = Field(default=RefundStatus.PENDING)

    # Provider's refund ID (from Paystack/Flutterwave API)
    external_refund_id: Optional[str] = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    payment: "Payment" = Relationship(back_populates="refunds")


# Add this relationship to your existing Payment model
# refunds: List["Refund"] = Relationship(back_populates="payment")
