from app.db.database import db
from app.models.schema import objects, checksums, access_methods, contents, datasets


async def get_db_objects(object_id: str):
    query = objects.select(objects.c.id == object_id)
    return await db.database.fetch_one(query)


async def get_checksum(object_id: str):
    query = checksums.select(checksums.c.object_id == object_id)
    return await db.database.fetch_all(query)

async def get_contents(object_id: str):
    query = contents.select(contents.c.object_id == object_id)
    return await db.database.fetch_all(query)

async def get_object_access_methods(object_id: str):
    query = access_methods.select(access_methods.c.object_id == object_id)
    return await db.database.fetch_all(query)

async def get_sub_objects(object_id: str):
    query = contents.select(contents.c.object_id == object_id)
    return await db.database.fetch_all(query)

async def get_objects_by_dataset(dataset_id: str, bundle_id: str):
    query = datasets.select(datasets.c.dataset == dataset_id, datasets.c.bundle == bundle_id)
    return await db.database.fetch_all(query)  