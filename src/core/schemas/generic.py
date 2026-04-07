from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

DataT = TypeVar('DataT')

class GenericResponse(BaseModel, Generic[DataT]):
    message: str = "Success"
    data: Optional[DataT] = None
