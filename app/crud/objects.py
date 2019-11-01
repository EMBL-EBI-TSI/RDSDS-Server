from fastapi import Depends
from app.db.database import get_database
from app.db.datamodels import objects, checksums, access_methods, contents

database = await get_database()

async def get_db_objects(object_id: str):
    query = objects.select(objects.c.id == object_id)
    return  database.fetch_one(query)


async def get_checksum(object_id: str):
    query = checksums.select(checksums.c.object_id == object_id)
    return await database.fetch_all(query)

async def get_contents(object_id: str):
    query = contents.select(contents.c.object_id == object_id)
    return await database.fetch_all(query)

async def get_object_access_methods(object_id: str):
    query = access_methods.select(access_methods.c.object_id == object_id)
    return await database.fetch_all(query)

async def get_sub_objects(object_id: str):
    query = contents.select(contents.c.object_id == object_id)
    return await database.fetch_all(query)
    