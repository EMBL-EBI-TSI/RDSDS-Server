from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.business import serviceinfo
from app.models.service import Service
from starlette.requests import Request

router = APIRouter()

@router.get(
    "",
    response_model=Service,
    response_model_skip_defaults=True,
    summary="Get info about a `Service`.",
    tags=["ServiceInfo"],
    name="get_service_info"
)
async def serviceInfo(request: Request):
    return await serviceinfo.get_service_info(request)
    