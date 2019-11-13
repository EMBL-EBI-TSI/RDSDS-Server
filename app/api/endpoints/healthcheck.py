from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

router = APIRouter()

@router.get(
    "/health-check",
    summary="Health Check",
    tags=["Health Check"],
)
async def healthCheck():
    return JSONResponse(status_code=200, content={
            "status_code": 200,
            "msg": "Health Check OK"
    })