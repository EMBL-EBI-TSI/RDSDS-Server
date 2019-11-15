from starlette.responses import JSONResponse


async def http_exception_handler(request, exc):
    return JSONResponse(
        {'msg': str(exc.detail), 'status_code': exc.status_code},
        status_code=exc.status_code
    )
    

