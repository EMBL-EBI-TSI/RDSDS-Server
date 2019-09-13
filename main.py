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

DATABASE_URL = "sqlite:///./data/dsds.db"
database = databases.Database(DATABASE_URL)
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

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
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
    #TODO; Fix id has to be required
    id: str = None
    drs_uri: str = None
    contents: Dict = None


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

# TOOD: Add List API
# @app.get("/ga4gh/drs/v1/objects", response_model=List[DRSObject])
# async def get_all_objects():
#     query = objects.select()
#     return await database.fetch_all(query)


@app.get(
    "/ga4gh/drs/v1/objects/{object_id}",
    response_model=DrsObject,
    response_model_skip_defaults=True,
    summary="Get info about a `DrsObject`.",
    tags=["DataRepositoryService"]
    # TODO: Add additional responses 202, 400, 401, 403, 500
    # https://fastapi.tiangolo.com/tutorial/additional-responses/
)
async def get_object(object_id: str, request: Request, expand: bool = False):
    """Returns object metadata, and a list of access methods that can be used to
     fetch object bytes."""
    client_host = request.client.host
    if request.client.port != 80:
        client_port = ":{}".format(request.client.port)
    else:
        client_port =""

    # Collecting DrsObject
    query = objects.select(objects.c.id == object_id).limit(1)
    object = await database.fetch_all(query)
    if not len(object):
        return JSONResponse(status_code=404, content={
            "status_code": 404,
            "msg": "Requested DrsObject was not found"
        })
        # raise HTTPException(status_code=404, detail="Requested DrsObject was not found")

    data = dict(object[0])
    # Generating DrsObject.self_url
    data['self_uri'] = "drs://{}{}/{}".format(client_host, client_port, data['id'])

    # Collecting DrsObject > Checksums
    query = checksums.select(checksums.c.object_id == object_id)
    object_checksums = await database.fetch_all(query)
    data['checksums'] = object_checksums

    # Collecting DrsObject > ContentObjects
    query = contents.select(contents.c.object_id == object_id)
    object_contents = await database.fetch_all(query)
    object_contents_list = []
    for oc in object_contents:
        # TODO: Recusive expansion of contents expand=true (currently only at depth=1)
        query = contents.select(contents.c.object_id == oc['id'])
        id_exists = await database.fetch_all(query)
        if len(id_exists):
            pprint(id_exists)

        object_contents_list.append({
            'name': oc['name'],
            'id': oc['id'],
            'drs_uri': "drs://{}{}/{}".format(client_host, client_port, oc['id']),
        })
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
