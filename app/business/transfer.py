from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.models.transfer import TransferBase, TransferType, TransferResponse
from app.models.objects import Error
from app.business import globus
from app.crud.objects import get_object_access_methods, get_contents


async def create_transfer(transferBase: TransferBase,  request: Request):
    """This function creates a transfer activity for an object"""
    transfer_type = transferBase.transfer_type
    # Code for globus
    if transfer_type == TransferType.GLOBUS:
        tokens = await globus.verify_globus_code(request)
        if not tokens:
            return JSONResponse(status_code=403, content={
                "status_code": 403,
                "msg": "The requester is not authorized to perform this action, Please login through /globus/login"
            })
        else:
            transfer_client = await globus.get_transfer_client(request)
            if not transferBase.source:
                if transferBase.object_id:
                    transferBase = await get_globus_source_from_object(transferBase)
                    isFolder = await check_if_bundle(transferBase.object_id)
            return await globus.create_transfer_globus(transferBase, transfer_client, isFolder)

async def check_if_bundle(object_id: str):
    """This function checks if an object is a bundle or not"""
    object_contents = await get_contents(object_id)
    if len(object_contents) == 0 :
        return False
    else:
        return True

async def get_globus_source_from_object(transferBase: TransferBase):
    """This function checks if an object have a globus source to transfer from"""
    object_access_methods = await get_object_access_methods(transferBase.object_id)
    for am in object_access_methods:
        if (am['type'] == TransferType.GLOBUS):
            #source_endpoint = source.split(':')[1].replace('/','')
            #source_path = source.split(':')[2]
            transferBase.source = am['access_url']
    return transferBase

async def get_transfer_list(request: Request):
    """This function checks for transfer list for an authenticated user"""
    transfer_status_list = []
    
    # Code for globus
    tokens = await globus.verify_globus_code(request)
    if tokens:
        globus_item_count = 10
        if 'globus_item_count' in request.query_params:
            globus_item_count = request.path_params['globus_item_count']
        transfer_client = await globus.get_transfer_client(request)
        transfer_response = await globus.get_transfer_globus_list(transfer_client, globus_item_count)
        transfer_status_list.append(transfer_response)
    else:
        error_response = {'globus' : 'No authorization available'}
        transfer_status_list.append(error_response)
    # TODO Other type of transfers
    
    transfer_status_json = jsonable_encoder(transfer_status_list)
    return JSONResponse(content=transfer_status_json, status_code=200)


async def get_transfer(transfer_id: str, request: Request):
    """This function checks for status for a transfer ID"""
    if transfer_id.startswith('globus'):
        tokens = await globus.verify_globus_code(request)
        if not tokens:
            return JSONResponse(status_code=403, content={
            "status_code": 403,
            "msg": "The requester is not authorized to perform this action, Please login through /globus/login"
        })
        else:
            globus_transfer_id = transfer_id.replace('globus-','')
            transfer_client = await globus.get_transfer_client(request)
            transfer_response = await globus.get_transfer_globus(globus_transfer_id, transfer_client)
            transfer_response_json = jsonable_encoder(transfer_response)
            return JSONResponse(content=transfer_response_json, status_code=transfer_response['status'])
    else:
        return None
    
    
async def delete_transfer(transfer_id: str, request: Request):
    """This function deletes/cancels a transfer ID"""
    if transfer_id.startswith('globus'):
        tokens = await globus.verify_globus_code(request)
        if not tokens:
            return JSONResponse(status_code=403, content={
            "status_code": 403,
            "msg": "The requester is not authorized to perform this action, Please login through /globus/login"
        })
        else:
            globus_transfer_id = transfer_id.replace('globus-','')
            transfer_client = await globus.get_transfer_client(request)
            transfer_response = await globus.delete_transfer_globus(globus_transfer_id, transfer_client)
            transfer_response_json = jsonable_encoder(transfer_response)
            return JSONResponse(content=transfer_response_json, status_code=transfer_response['status'])
    else:
        return None