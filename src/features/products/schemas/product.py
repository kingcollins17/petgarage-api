from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from .category import CategoryRead

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int
    
class ProductCreate(ProductBase):
    category_ids: List[int] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    category_ids: Optional[List[int]] = None
    
class ProductRead(ProductBase):
    id: int
    vendor_id: int
    categories: List[CategoryRead] = []
    
    model_config = ConfigDict(from_attributes=True)
