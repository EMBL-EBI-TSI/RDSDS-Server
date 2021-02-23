from app.crud.datasets import get_objects_by_dataset
from starlette.responses import JSONResponse
from app.business.objects import get_objects

async def get_objects_by_omics(dataset_id: str, bundle_id: str, client_host: str):
    object_list = await get_objects_by_dataset(dataset_id,bundle_id)
    if not object_list:
        return JSONResponse(status_code=404, content={
            "status_code": 404,
            "msg": "Requested Dataset was not found"
        })
    new_object_list = []
    for object in object_list:
      new_object = get_objects(object_id=object['object_id'], client_host=client_host)
      new_object_list += new_object

    print(new_object_list)
    return new_object_list
    