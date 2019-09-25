import os
from datetime import datetime
from enum import Enum
from pprint import pprint
from typing import Dict, List

import databases
import sqlalchemy
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.gzip import GZipMiddleware

from dotenv import load_dotenv
from pathlib import Path  # python3 only
env_path = Path('.env')
load_dotenv(dotenv_path=env_path)

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT", 5000))
DATABASE_URL = os.getenv("DATABASE_URL")


database = databases.Database(DATABASE_URL.replace("postgres://","postgresql://"))
metadata = sqlalchemy.MetaData()

objects = sqlalchemy.Table(
    "objects",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("self_uri", sqlalchemy.String),
    sqlalchemy.Column("size", sqlalchemy.BigInteger),
    sqlalchemy.Column("created_time", sqlalchemy.DateTime),
    sqlalchemy.Column("updated_time", sqlalchemy.DateTime),
    sqlalchemy.Column("version", sqlalchemy.String),
    sqlalchemy.Column("mime_type", sqlalchemy.String),
    sqlalchemy.Column("aliases", sqlalchemy.String),
)

checksums = sqlalchemy.Table(
    "checksums",
    metadata,
    sqlalchemy.Column("object_id", sqlalchemy.String),
    sqlalchemy.Column("type", sqlalchemy.String),
    sqlalchemy.Column("checksum", sqlalchemy.String),
)

access_methods = sqlalchemy.Table(
    "access_methods",
    metadata,
    sqlalchemy.Column("object_id", sqlalchemy.String),
    sqlalchemy.Column("type", sqlalchemy.String),
    sqlalchemy.Column("access_url", sqlalchemy.String),
    sqlalchemy.Column("region", sqlalchemy.String),
    sqlalchemy.Column("headers", sqlalchemy.String),
    sqlalchemy.Column("access_id", sqlalchemy.String),
)

contents = sqlalchemy.Table(
    "contents",
    metadata,
    sqlalchemy.Column("object_id", sqlalchemy.String),
    sqlalchemy.Column("id", sqlalchemy.String),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("drs_uri", sqlalchemy.String),
)


router = APIRouter()

app = FastAPI()
app.add_middleware(GZipMiddleware)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)


class Checksum(BaseModel):
    type: str
    checksum: str


class AccessMethodEnum(str, Enum):
    s3 = 's3'
    gs = 'gs'
    ftp = 'ftp'
    #TODO: Update spec for sftp support
    sftp = 'sftp'
    gsiftp = 'gsiftp'
    globus = 'globus'
    htsget = 'htsget'
    https = 'https'
    file = 'file'


class AccessURL(BaseModel):
    url: str
    headers: Dict[str, str] = None


class AccessMethod(BaseModel):
    type: AccessMethodEnum
    access_url: AccessURL
    access_id: str = None
    region: str = None


class ContentsObject(BaseModel):
    name: str
    #TODO: Fix id has to be required in spec
    id: str
    drs_uri: str = None
    contents: List['ContentsObject'] = None


ContentsObject.update_forward_refs()


class DrsObject(BaseModel):
    id: str
    name: str
    self_uri: str
    size: int
    created_time: datetime = None
    updated_time: datetime = None
    version: str = None
    mime_type: str = None
    checksums: List[Checksum] = []
    access_methods: List[AccessMethod] = []
    contents: List[ContentsObject] = []
    description: str = None
    aliases: List[str] = None

class Error(BaseModel):
    msg: str
    status_code: int = 500


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Reference Data Set Distribution Service",
        description="Provides a GA4GH DRS compatible interface datasets stored within the ELIXIR network",
        version="2.0.0",
        routes=app.routes,
    )
    openapi_schema['basePath'] = "/ga4gh/drs/v1"
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        {'msg': str(exc.detail), 'status_code': exc.status_code},
        status_code=exc.status_code
    )


@app.get(
    "/",
    summary="Health Check",
    # TODO: Add additional responses 202, 400, 401, 403, 500
    # https://fastapi.tiangolo.com/tutorial/additional-responses/
)
async def healthCheck():
    return JSONResponse(status_code=200, content={
            "status_code": 200,
            "msg": "Health Check OK"
    })
        
        
async def collect_sub_objects(client_host, object_id):
    #global client_host
    #global client_port
    sub_objects_list = []
    query = contents.select(contents.c.object_id == object_id)
    sub_objects = await database.fetch_all(query)
    if len(sub_objects):
        for sub_obj in sub_objects:
            so = dict(sub_obj)
            sub_contents = await collect_sub_objects(so['id'])
            sub_objects_list.append({
                'name': os.path.basename(so['name']),
                'id': so['id'],
                'drs_uri': "drs://{}/{}".format(client_host, so['id']),
                'contents': sub_contents
            })
    else:
        return None
    return sub_objects_list

@app.get(
    "/ga4gh/drs/v1/objects/{object_id}",
    response_model=DrsObject,
    response_model_skip_defaults=True,
    summary="Get info about a `DrsObject`.",
    tags=["DataRepositoryService"],
    responses={
        201: {'model': Error, 'description': "The operation is delayed and will continue asynchronously. The client should retry this same request after the delay specified by Retry-After header."},
        400: {'model': Error, 'description': "The request is malformed."},
        401: {'model': Error, 'description': "The request is unauthorized."},
        403: {'model': Error, 'description': "The requester is not authorized to perform this action."},
        404: {'model': Error, 'description': "The requested `DrsObject` wasn't found"},
        500: {'model': Error, 'description': "An unexpected error occurred."}
    }
)
async def get_object(object_id: str, request: Request, expand: bool = False):
    """Returns object metadata, and a list of access methods that can be used to
     fetch object bytes."""
    #global client_host
    #global client_port
    #print(request.headers)
    
    client_host = request.headers['host']
    #print(client_host)
    #if request.client.port != 80:
    #    client_port = ":{}".format(request.client.port)
    #else:
    #    client_port =""

    # Collecting DrsObject
    query = objects.select(objects.c.id == object_id)
    object = await database.fetch_one(query)
    if not object:
        return JSONResponse(status_code=404, content={
            "status_code": 404,
            "msg": "Requested DrsObject was not found"
        })

    data = dict(object)
    # Generating DrsObject.self_url
    data['self_uri'] = "drs://{}/{}".format(client_host, data['id'])

    # Collecting DrsObject > Checksums
    query = checksums.select(checksums.c.object_id == object_id)
    object_checksums = await database.fetch_all(query)
    data['checksums'] = object_checksums

    # Collecting DrsObject > ContentObjects
    query = contents.select(contents.c.object_id == object_id)
    object_contents = await database.fetch_all(query)
    object_contents_list = []
    for oc in object_contents:
        d = {
            'name': oc['name'],
            'id': oc['id'],
            'drs_uri': "drs://{}/{}".format(client_host, oc['id'])
        }
        # (if expand=true) Collecting Recursive DrsObject > ContentObjects
        if expand:
            d['contents'] = await collect_sub_objects(client_host, oc['id'])
        # Add object > content to list
        object_contents_list.append(d)
    data['contents'] = object_contents_list

    # Collecting DrsObject > AccessMethods
    query = access_methods.select(access_methods.c.object_id == object_id)
    object_access_methods = await database.fetch_all(query)
    object_access_method_list = []
    for am in object_access_methods:
        object_access_method_list.append({
            'type': am['type'],
            'access_url': {
                'url': am['access_url'],
                'headers': am['headers']
            },
            'access_id': am['access_id'],
            'region': am['region']
        })
    data['access_methods'] = object_access_method_list

    return data


@app.get(
    "/ga4gh/drs/v1/objects/{object_id}/access/{access_id}",
    response_model=AccessURL,
    summary="Get a URL for fetching bytes.",
    tags=["DataRepositoryService"]
)
async def get_object_access(object_id: str, access_id: str):
    """Returns a URL that can be used to fetch the bytes of a `DrsObject`.
    This method only needs to be called when using an `AccessMethod` that contains
    an `access_id` (e.g., for servers that use signed URLs for fetching object bytes).
    """
    raise HTTPException(status_code=501, detail="Access API Path not Implemented")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)