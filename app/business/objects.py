import logging
import os

from app.db.database import DataBase, get_database
from app.db.datamodels import objects, checksums, access_methods, contents
from fastapi import Depends
from starlette.responses import JSONResponse
from app.db.database import db as database



async def get_objects(object_id: str, client_host: str, expand: bool=False, database: DataBase=Depends(get_database)):
    """Returns dbObject metadata, and a list of access methods that can be used to
     fetch dbObject bytes."""
    # Collecting DrsObject
    query = objects.select(objects.c.id == object_id)
    dbObject = await database.fetch_one(query)
    logging.info(dbObject)
    if not dbObject:
        return JSONResponse(status_code=404, content={
            "status_code": 404,
            "msg": "Requested DrsObject was not found"
        })

    data = dict(dbObject)
    # Generating DrsObject.self_url
    data['self_uri'] = "drs://{}/{}".format(client_host, data['id'])

    # Collecting DrsObject > Checksums
    query = checksums.select(checksums.c.object_id == object_id)
    object_checksums = await database.fetch_all(query)
    data['checksums'] = object_checksums

    # Collecting DrsObject > ContentObjects
    query = contents.select(contents.c.object_id == object_id)
    object_contents = await database.fetch_all(query)
    object_contents_list = []
    for oc in object_contents:
        d = {
            'name': oc['name'],
            'id': oc['id'],
            'drs_uri': "drs://{}/{}".format(client_host, oc['id'])
        }
        # (if expand=true) Collecting Recursive DrsObject > ContentObjects
        if expand:
            d['contents'] = await collect_sub_objects(client_host, oc['id'])
        # Add dbObject > content to list
        object_contents_list.append(d)
    data['contents'] = object_contents_list

    # Collecting DrsObject > AccessMethods
    query = access_methods.select(access_methods.c.object_id == object_id)
    object_access_methods = await database.fetch_all(query)
    object_access_method_list = []
    for am in object_access_methods:
        object_access_method_list.append({
            'type': am['type'],
            'access_url': {
                'url': am['access_url'],
                'headers': am['headers']
            },
            'access_id': am['access_id'],
            'region': am['region']
        })
    data['access_methods'] = object_access_method_list

    return data


async def collect_sub_objects(client_host, object_id):
    # global client_host
    # global client_port
    sub_objects_list = []
    query = contents.select(contents.c.object_id == object_id)
    sub_objects = await database.fetch_all(query)
    if len(sub_objects):
        for sub_obj in sub_objects:
            so = dict(sub_obj)
            sub_contents = await collect_sub_objects(so['id'])
            sub_objects_list.append({
                'name': os.path.basename(so['name']),
                'id': so['id'],
                'drs_uri': "drs://{}/{}".format(client_host, so['id']),
                'contents': sub_contents
            })
    else:
        return None
    return sub_objects_list
