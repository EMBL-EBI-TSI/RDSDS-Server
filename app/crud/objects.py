from app.db.database import get_database
from app.db.datamodels import objects, checksums, access_methods, contents


async def get_db_objects(object_id: str):
    database = await get_database()
    query = objects.select(objects.c.id == object_id)
    return  database.fetch_one(query)


async def get_checksum(object_id: str):
    database = await get_database()
    query = checksums.select(checksums.c.object_id == object_id)
    return await database.fetch_all(query)

async def get_contents(object_id: str):
    database = await get_database()
    query = contents.select(contents.c.object_id == object_id)
    return await database.fetch_all(query)

async def get_object_access_methods(object_id: str):
    database = await get_database()
    query = access_methods.select(access_methods.c.object_id == object_id)
    return await database.fetch_all(query)

async def get_sub_objects(object_id: str):
    database = await get_database()
    query = contents.select(contents.c.object_id == object_id)
    return await database.fetch_all(query)
    