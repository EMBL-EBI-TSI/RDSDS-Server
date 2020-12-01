from fastapi import APIRouter, HTTPException
from app.models.datasets import Datasets
from app.business import datasets
from typing import Dict, List

router = APIRouter()

@router.get(
    "/{dataset_id}/{bundle_id}",
    response_model=List[Datasets],
    summary="Get a URL for fetching bytes.",
    tags=["OmicsIntegration"]
)
async def get_objects_by_omics(dataset_id: str, bundle_id: str):
    """Returns a list of Objects for the dataset
    """
    data = await datasets.get_datasets_by_omics(dataset_id=dataset_id, bundle_id=bundle_id)
    print(data)
    return data