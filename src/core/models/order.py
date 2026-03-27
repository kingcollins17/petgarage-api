class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customerprofile.id")
    total_amount: float
    status: OrderStatus = Field(default=OrderStatus.PENDING)

    # Paystack Reference
    payment_reference: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    unit_price: float  # Snapshot of price at time of purchase

    order: Order = Relationship(back_populates="items")
