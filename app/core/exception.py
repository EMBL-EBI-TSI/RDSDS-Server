import logging
import traceback
from starlette.responses import JSONResponse

async def http_exception_handler(request, exc):
    message = [str(x) for x in exc.args]
    status_code = 400
    success = False
    response = {
        'success': success,
        'error': {
            'type': exc.__class__.__name__,
            'message': message
        }
    }
    logging.error('Error occured:{}'.format(traceback.format_exc()))
    return JSONResponse(
        response,
        status_code=status_code
    )

