from fastapi import APIRouter, Depends


router = APIRouter()

@router.get(
    "/health-check",
    summary="Health Check",
    # TODO: Add additional responses 202, 400, 401, 403, 500
    # https://fastapi.tiangolo.com/tutorial/additional-responses/
)
async def healthCheck():
    return JSONResponse(status_code=200, content={
            "status_code": 200,
            "msg": "Health Check OK"
    })