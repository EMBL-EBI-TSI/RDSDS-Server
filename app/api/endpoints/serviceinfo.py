from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.models.service import Service

router = APIRouter()

@router.get(
    "",
    response_model=Service,
    response_model_skip_defaults=True,
    summary="Get info about a `Service`.",
    tags=["ServiceInfo"],
    name="get_service_info"
)
async def serviceInfo():
    serviceInfo = Service()
    