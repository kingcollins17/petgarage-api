from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

DataT = TypeVar('DataT')

class GenericResponse(BaseModel, Generic[DataT]):
    message: str = "Success"
    data: Optional[DataT] = None


class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int


class PaginatedResponse(GenericResponse[DataT]):
    metadata: Optional[PaginationMeta] = None
