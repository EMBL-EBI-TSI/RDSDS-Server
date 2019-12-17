from fastapi import APIRouter, HTTPException
from app.models.objects import DrsObject, Error, AccessURL
from app.business import objects
from app.business.oauth import auth_request
from starlette.requests import Request

router = APIRouter()


@router.get(
    "/objects/{object_id}",
    response_model=DrsObject,
    response_model_skip_defaults=True,
    summary="Get info about a `DrsObject`.",
    tags=["DataRepositoryService"],
    name="get_object",
    responses={
        201: {'model': Error, 'description': "The operation is delayed and will continue asynchronously. The client should retry this same request after the delay specified by Retry-After header."},
        400: {'model': Error, 'description': "The request is malformed."},
        401: {'model': Error, 'description': "The request is unauthorized."},
        403: {'model': Error, 'description': "The requester is not authorized to perform this action."},
        404: {'model': Error, 'description': "The requested `DrsObject` wasn't found"},
        500: {'model': Error, 'description': "An unexpected error occurred."}
    }
)
async def get_object(object_id: str, request: Request):
    """Returns object metadata, and a list of access methods that can be used to
     fetch object bytes."""
    client_host = request.headers['host']

    # Collecting DrsObject
    data = await objects.get_objects(object_id=object_id, client_host=client_host, expand=True)

    return data


@router.get(
    "/objects/{object_id}/access/{access_id}",
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
