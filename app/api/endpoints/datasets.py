from fastapi import APIRouter, HTTPException
from app.models.datasets import Datasets
from app.business import datasets
from typing import Dict, List
from starlette.requests import Request

router = APIRouter()

@router.get(
    "/{dataset_id}/{bundle_id}",
    response_model=List[Datasets],
    summary="Get a URL for fetching bytes.",
    tags=["OmicsIntegration"]
)
async def get_objects_by_omics(dataset_id: str, bundle_id: str, request: Request):
    """Returns a list of Objects for the dataset
    """
    client_host = request.headers['host']
    client_scheme = request.url.scheme
    data = await datasets.get_objects_by_omics(dataset_id=dataset_id, bundle_id=bundle_id, client_host=client_host, client_scheme=client_scheme)
    print(data)
    return data