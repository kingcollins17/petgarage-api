import enum
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel


class ProductCategory(str, enum.Enum):
    PET = "pet"
    SUPPLY = "supply"


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    price: float
    stock_quantity: int
    category: ProductCategory
    vendor_id: int = Field(foreign_key="vendorprofile.id")

    vendor: "VendorProfile" = Relationship(back_populates="products")
    # Specific details for pets
    pet_details: Optional["PetDetail"] = Relationship(back_populates="product")


class PetDetail(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    species: str  # e.g., Dog, Cat
    breed: str
    age_months: int
    gender: str
    is_vaccinated: bool = True
    product_id: int = Field(foreign_key="product.id")

    product: Product = Relationship(back_populates="pet_details")
