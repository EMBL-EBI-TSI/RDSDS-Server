from app.crud.datasets import get_objects_by_dataset

async def get_objects_by_omics(dataset_id: str, bundle_id: str):
    object_list= []
    object_list = get_objects_by_dataset(dataset_id,bundle_id)
    return object_list
    