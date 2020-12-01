from app.crud.datasets import get_objects_by_dataset
from starlette.responses import JSONResponse

async def get_objects_by_omics(dataset_id: str, bundle_id: str):
    object_list = await get_objects_by_dataset(dataset_id,bundle_id)
    if not object_list:
        return JSONResponse(status_code=404, content={
            "status_code": 404,
            "msg": "Requested Dataset was not found"
        })
    print(dict(object_list))
    return dict(object_list)
    