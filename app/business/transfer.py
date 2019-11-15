import json
import logging
from globus_sdk import (TransferClient, GlobusError, GlobusAPIError, NetworkError, TransferData, AccessTokenAuthorizer)
from datetime import datetime
from fastapi import Header, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from app.models.transfer import TransferBase


async def verify_globus_code(request: Request):
    """This function verifies if globus authentication is present in session"""
    tokens = request.session.get('tokens', False)
    if tokens:
        return tokens
    else:
        return False
    
    
    
async def get_transfer_client(request: Request):
    """This function forms globus transfer client with authentication present in session token"""
    tokens = request.session.get('tokens', False)
    authorizer = AccessTokenAuthorizer(tokens['transfer.api.globus.org']['access_token'])
    transfer_client = TransferClient(authorizer=authorizer)
    return transfer_client
  
  
    
def handle_globus_api_error(e:GlobusAPIError):
    """This function handles any error received from Globus"""
    logging.error(("Got a Globus API Error\n"
                       "Error Code: {}\n"
                       "Error Message: {}").format(e.code, e.message))
        
    transfer_response = {'msg': e.message}
    transfer_response['status_code'] = e.http_status 
    
    return transfer_response



async def create_transfer_globus(transferObject: TransferBase, transfer_client: TransferClient ):
    """This function verifies if globus authentication is present in session"""
    #transfer_client = await get_transfer_client(request)
    logging.info(transferObject.options)
    source_endpoint_id = transferObject.options['source_endpoint']
    destination_endpoint_id = transferObject.options['destination_endpoint']
    source = transferObject.source
    target = transferObject.target
    
    transfer_response = None
    
    isFolder = False
    
    if 'recursive' in transferObject.options:
        if transferObject.options['recursive'] == "True":
            isFolder = True
    
    time = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
    
    try:
            
        tdata = TransferData(transfer_client, source_endpoint_id,
                                        destination_endpoint_id,
                                        label= 'RDSDS ' + time,
                                        sync_level="checksum")
        
        
        if isFolder:
            tdata.add_item(source, target, recursive=True)
        else:
            tdata.add_item(source, target)
            
        transfer_result = transfer_client.submit_transfer(tdata)
        transfer_result_json = json.loads(str(transfer_result))
        
        
        transfer_response = {'globus_response': transfer_result_json}
        transfer_response['status'] = 200
        rdsds_tracking_id = 'globus-' + transfer_result["task_id"]
        transfer_response['rdsds_tracking_id'] = rdsds_tracking_id
        transfer_response['globus_status_url'] = 'https://app.globus.org/activity/' + transfer_result["task_id"] + '/overview'
        
        return transfer_response
    
    except GlobusAPIError as e:
        # Error response from the REST service, check the code and message for
        # details.        
        return handle_globus_api_error(e)
    except NetworkError:
        logging.error(("Network Failure. "
                       "Possibly a firewall or connectivity issue"))
        raise
    except GlobusError:
        logging.exception("Totally unexpected GlobusError!")
        raise


async def get_transfer_globus(globus_transfer_id: str, transfer_client: TransferClient ):
    """This function gets status of globus transfer"""
    #transfer_client = await get_transfer_client(request)
    transfer_response = None
    
    try:
            
        transfer_result = transfer_client.get_task(globus_transfer_id)
        transfer_result_json = json.loads(str(transfer_result))
        transfer_response = {'globus_response': transfer_result_json}
        transfer_response['status'] = 200
        
        return transfer_response
    
    except GlobusAPIError as e:
        # Error response from the REST service, check the code and message for
        # details.
        # Error response from the REST service, check the code and message for
        # details.        
        return handle_globus_api_error(e)
        
        return transfer_response
    except NetworkError:
        logging.error(("Network Failure. "
                       "Possibly a firewall or connectivity issue"))
        raise
    except GlobusError:
        logging.exception("Totally unexpected GlobusError!")
        raise


async def delete_transfer_globus(globus_transfer_id: str, transfer_client: TransferClient ):
    """This function cancels a globus transfer"""
    #transfer_client = await get_transfer_client(request)
    transfer_response = None
    
    try:
        transfer_result = transfer_client.cancel_task(globus_transfer_id)
        transfer_result_json = json.loads(str(transfer_result))
        transfer_response = {'globus_response': transfer_result_json}
        transfer_response['status'] = 200
        
        return transfer_response
    
    except GlobusAPIError as e:
        # Error response from the REST service, check the code and message for
        # details.
        return handle_globus_api_error(e)
    except NetworkError:
        logging.error(("Network Failure. "
                       "Possibly a firewall or connectivity issue"))
        raise
    except GlobusError:
        logging.exception("Totally unexpected GlobusError!")
        raise