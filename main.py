from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from app.api.endpoints.objects import router as api_router
from app.api.endpoints.healthcheck import router as healthcheck_router
from app.core.config import API_V1_STR, PROJECT_NAME, HOST, PORT
from app.db.db_utils import close_postgres_connection, connect_to_postgres
from app.core.openapi import custom_openapi
from app.core.exception import http_exception_handler

app = FastAPI(title=PROJECT_NAME)

app.add_event_handler("startup", connect_to_postgres)
app.add_event_handler("shutdown", close_postgres_connection)

app.add_exception_handler(HTTPException, http_exception_handler)

app.include_router(api_router, prefix=API_V1_STR)
app.include_router(healthcheck_router, prefix="/")

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
