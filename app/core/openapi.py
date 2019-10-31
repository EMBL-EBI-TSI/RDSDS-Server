from fastapi import FastAPI

from app.core.config import API_V1_STR
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Reference Data Set Distribution Service",
        description="Provides a GA4GH DRS compatible interface datasets stored within the ELIXIR network",
        version="2.0.0",
        routes=app.routes,
    )
    openapi_schema['basePath'] = API_V1_STR
    app.openapi_schema = openapi_schema
    return app.openapi_schema
