from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: Any) -> Optional[ModelType]:
        """Fetch a single record by its primary key."""
        return await self.db.get(self.model, id)

    async def list(self, page: int = 1, per_page: int = 100) -> List[ModelType]:
        """Fetch a list of records with pagination."""
        offset = (page - 1) * per_page
        statement = select(self.model).offset(offset).limit(per_page)
        results = await self.db.execute(statement)
        return results.scalars().all()

    async def create(self, obj_in: ModelType) -> ModelType:
        """Create a new record in the database."""
        self.db.add(obj_in)
        await self.db.commit()
        await self.db.refresh(obj_in)
        return obj_in

    async def update(
        self, db_obj: ModelType, obj_in: Union[ModelType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record."""
        obj_data = db_obj.model_dump()
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any) -> Optional[ModelType]:
        """Delete a record by its primary key."""
        obj = await self.db.get(self.model, id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
        return obj
