from fastapi import APIRouter, Depends
from app.db.database import db as database
from app.models.objects import DrsObject, Error, AccessURL
import app.db.datamodels

router = APIRouter()


@router.get(
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
    client_host = request.headers['host']

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


@router.get(
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
