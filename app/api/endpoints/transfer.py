
from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.models.transfer import TransferBase, TransferType, TransferResponse
from app.business.oauth import auth_request
from app.models.objects import Error
from app.business import transfer

router = APIRouter()

@router.post(
    "",
    summary="Create a transfer request for RDSDS",
    name='create_transfer_globus',
    tags=["TransferService"],
    response_model=TransferResponse,
    response_model_skip_defaults=True,
    responses={
        403: {'model': Error, 'description': "The requester is not authorized to perform this action, Please login through /globus/login"},
        500: {'model': Error, 'description': "An unexpected error occurred."}
    }
)
async def create_transfer(transferBase: TransferBase,  request: Request, auth: bool = Depends(auth_request)):
    if auth:
        return await transfer.create_transfer(transferBase,  request)
    else:
        return JSONResponse(status_code=403, content={
            "status_code": 403,
            "msg": "The requester is not authorized to perform this action, Please login through /oauth/login"
        })


@router.get(
    "/",
    summary="Get list for transfers for RDSDS",
    name='get_transfer_list',
    tags=["TransferService"],
    responses={
        403: {'model': Error, 'description': "The requester is not authorized to perform this action, Please login through /globus/login"},
        500: {'model': Error, 'description': "An unexpected error occurred."}
    }
)        
async def get_transfer_list(request: Request):
    return await transfer.get_transfer_list(request)
    
@router.get(
    "/{transfer_id}",
    summary="Get status for transfer request for RDSDS",
    name='get_transfer',
    tags=["TransferService"],
    responses={
        403: {'model': Error, 'description': "The requester is not authorized to perform this action, Please login through /globus/login"},
        500: {'model': Error, 'description': "An unexpected error occurred."}
    }
)        
async def get_transfer(transfer_id: str, request: Request):
    return await transfer.get_transfer(transfer_id, request)
    


@router.delete(
    "/{transfer_id}",
    summary="Cancel transfer request for RDSDS",
    name='delete_transfer',
    tags=["TransferService"],
    responses={
        403: {'model': Error, 'description': "The requester is not authorized to perform this action, Please login through /globus/login"},
        500: {'model': Error, 'description': "An unexpected error occurred."}
    }
)        
async def delete_transfer(transfer_id: str, request: Request):
    return await transfer.delete_transfer(transfer_id, request)
       