from src.core.models.product import Product, PetDetail
from src.core.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db):
        super().__init__(Product, db)


class PetDetailRepository(BaseRepository[PetDetail]):
    def __init__(self, db):
        super().__init__(PetDetail, db)
