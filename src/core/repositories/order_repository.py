from typing import List, Optional
from sqlmodel import select
from src.core.models.order import Order, OrderItem
from src.core.models.payment import Payment
from src.core.models.refund import Refund
from src.core.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db):
        super().__init__(Order, db)

    async def get_by_reference(self, reference: str) -> Optional[Order]:
        """Fetch an order by its payment reference."""
        statement = select(Order).where(Order.payment_reference == reference)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()


class OrderItemRepository(BaseRepository[OrderItem]):
    def __init__(self, db):
        super().__init__(OrderItem, db)


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db):
        super().__init__(Payment, db)

    async def get_by_external_reference(self, reference: str) -> Optional[Payment]:
        """Fetch a payment by its external provider reference."""
        statement = select(Payment).where(Payment.external_reference == reference)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()


class RefundRepository(BaseRepository[Refund]):
    def __init__(self, db):
        super().__init__(Refund, db)
