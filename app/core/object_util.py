import os

from app.db.database import db as database
import app.models.objects.contents


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
