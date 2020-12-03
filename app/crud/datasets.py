from app.db.database import db
from sqlalchemy.sql import and_
from app.models.schema import datasets


async def get_objects_by_dataset(dataset_id: str, bundle_id: str):
    query = datasets.select(and_(datasets.c.dataset == dataset_id, datasets.c.bundle == bundle_id))
    return await db.database.fetch_all(query) 


async def get_object_meta(object_id: str):
    query = datasets.select(datasets.c.object_id == object_id)
    return await db.database.fetch_one(query)