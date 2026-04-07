from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import Field, Relationship, SQLModel


class ProductCategoryLink(SQLModel, table=True):
    """Many-to-many link table between Product and Category."""

    product_id: int = Field(foreign_key="product.id", primary_key=True)
    category_id: int = Field(foreign_key="category.id", primary_key=True)


class Category(SQLModel, table=True):
    """A product category stored in the database."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Many-to-many relationship with products
    products: List["Product"] = Relationship(
        back_populates="categories", link_model=ProductCategoryLink
    )

    def __repr__(self) -> str:
        return f"<Category(name={self.name})>"


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    price: float
    stock_quantity: int
    vendor_id: int = Field(foreign_key="vendorprofile.id")

    vendor: "VendorProfile" = Relationship(back_populates="products")
    # Specific details for pets
    pet_details: Optional["PetDetail"] = Relationship(back_populates="product")

    # Many-to-many relationship with categories
    categories: List[Category] = Relationship(
        back_populates="products", link_model=ProductCategoryLink
    )


class PetDetail(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    species: str  # e.g., Dog, Cat
    breed: str
    age_months: int
    gender: str
    is_vaccinated: bool = True
    product_id: int = Field(foreign_key="product.id")

    product: Product = Relationship(back_populates="pet_details")
