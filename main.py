# This work is co-funded by the EOSC-hub project (Horizon 2020) under Grant number 777536.

import logging

from app.api.endpoints.healthcheck import router as healthcheck_router
from app.api.endpoints.objects import router as api_router
from app.api.endpoints.transfer import router as transfer_router
from app.api.endpoints.globus import router as globus_router
from app.api.endpoints.oauth import router as oauth_router
from app.api.endpoints.serviceinfo import router as service_info_router
from app.api.endpoints.datasets import router as datasets_router
from app.core.config import API_V1_STR, PROJECT_NAME, HOST, PORT, SESSION_SECRET_KEY
from app.core.exception import http_exception_handler
from app.business.globus_client import load_app_client
from app.business.oauth_client import load_oauth_client
from app.business.serviceinfo import create_service_info
#from core.openapi import custom_openapi#
from app.db.db_utils import close_postgres_connection, connect_to_postgres
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.sessions import SessionMiddleware

# from app.core.openapi import custom_openapi
app = FastAPI(title=PROJECT_NAME)

app.add_event_handler("startup", connect_to_postgres)
app.add_event_handler("startup", load_app_client)
app.add_event_handler("startup", load_oauth_client)
app.add_event_handler("startup", create_service_info)

app.add_event_handler("shutdown", close_postgres_connection)

app.add_exception_handler(Exception, http_exception_handler)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Reference Data Set Distribution Service",
        description="Provides a GA4GH DRS compatible interface datasets stored within the ELIXIR network. This work is co-funded by the EOSC-hub project (Horizon 2020) under Grant number 777536.",
        version="2.0.0",
        routes=app.routes
    )
    openapi_schema['basePath'] = API_V1_STR
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(api_router, prefix=API_V1_STR)
app.include_router(healthcheck_router, prefix='/health-check')
app.include_router(transfer_router, prefix='/transfer')
app.include_router(globus_router, prefix='/globus')
app.include_router(oauth_router, prefix='/oauth')
app.include_router(service_info_router, prefix='/service-info')
app.include_router(datasets_router, prefix='/datasets')

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
