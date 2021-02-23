from app.crud.datasets import get_objects_by_dataset
from starlette.responses import JSONResponse
from app.business.objects import get_objects

async def get_objects_by_omics(dataset_id: str, bundle_id: str, client_host: str, client_scheme: str):
    object_list = await get_objects_by_dataset(dataset_id,bundle_id)
    if not object_list:
        return JSONResponse(status_code=404, content={
            "status_code": 404,
            "msg": "Requested Dataset was not found"
        })
    new_object_list = []

    for object in object_list:
      new_object = dict()
      new_object['drsURI'] = "drs://{}/{}".format(client_host, object['object_id'])
      new_object['drsURL'] = "{}://{}/ga4gh/drs/v1/objects/{}".format(client_scheme,client_host, object['object_id'])
      for key in object.keys():
        new_object[key] = object[key]
      print(new_object)
      new_object_list.append(new_object)

    print(new_object_list)
    return new_object_list
    