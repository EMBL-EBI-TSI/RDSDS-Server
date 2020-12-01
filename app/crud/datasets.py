from app.db.database import db
from app.models.schema import datasets


async def get_objects_by_dataset(dataset_id: str, bundle_id: str):
    query = datasets.select(datasets.c.dataset == dataset_id, datasets.c.bundle == bundle_id)
    return await db.database.fetch_all(query) 