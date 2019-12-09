import logging
import json

from globus_sdk import (TransferClient, GlobusError, GlobusAPIError, NetworkError, TransferData, AccessTokenAuthorizer)
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from app.business.globus_client import globus
from app.models.transfer import TransferBase
from datetime import datetime
from fastapi.encoders import jsonable_encoder

    
async def login(request: Request):
    hostedServer = False
    
    if 'localhost:' not in request.headers.get('Host',''):
        hostedServer = True 
    
    # the redirect URI, as a complete URI (not relative path)
    redirect_uri = request.url_for('globus_login')
    if hostedServer:
        redirect_uri = redirect_uri.replace('http:','https:')
    globus.client.oauth2_start_flow(redirect_uri)

    # If there's no "code" query string parameter, we're in this route
    # starting a Globus Auth login flow.
    # Redirect out to Globus Auth
    if 'code' not in request.query_params:
        auth_uri = globus.client.oauth2_get_authorize_url()
        return RedirectResponse(auth_uri)
    # If we do have a "code" param, we're coming back from Globus Auth
    # and can start the process of exchanging an auth code for a token.
    else:
        jsonResponse = { 'Process' : 'Globus_Auth'}
        code = request.query_params['code']
        try:
            tokens = globus.client.oauth2_exchange_code_for_tokens(code)
    
            # store the resulting tokens in the session
            request.session.update(
                tokens=tokens.by_resource_server,
                is_authenticated=True
            )
        except GlobusAPIError as e:
            # Error response from the REST service, check the code and message for
            # details.
            logging.error(("Got a Globus API Error\n"
                           "Error Code: {}\n"
                           "Error Message: {}").format(e.code, e.message))
            
            jsonResponse = {'Globus_code': e.code}
            jsonResponse['Globus_error'] = e.message
            jsonResponse['status'] = e.http_status 
            
            return jsonResponse
        except NetworkError:
            logging.error(("Network Failure. "
                           "Possibly a firewall or connectivity issue"))
            raise
        except GlobusError:
            logging.exception("Totally unexpected GlobusError!")
            raise
        
        jsonResponse['login_success'] = True
        jsonResponse['status'] = 200
        jsonResponse_json = jsonable_encoder(jsonResponse)
        return JSONResponse(content=jsonResponse_json, status_code=jsonResponse['status'])
    

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



async def create_transfer_globus(transferObject: TransferBase, transfer_client: TransferClient , isFolder: bool = False):
    """This function verifies if globus authentication is present in session"""
    #transfer_client = await get_transfer_client(request)
    source = transferObject.source
    target = transferObject.target
    source_name = ''
    source_path = ''
    # example source: globus://fd9c190c-b824-11e9-98d7-0a63aa6b37da:/gridftp/pub/databases/eva/PRJEB6057/MOCH.population_sites.CHIR1_0.20140307_EVA_ss_IDs.fixed.vcf.gz
    if source:
        source_endpoint_id = source.split(':')[1].replace('/','')
        source_path = source.split(':')[2]
        source_path_array = source_path.split('/')
        source_name = source_path_array[len(source_path_array)-1]
    
    if target:
        target_endpoint_id = target.split(':')[1].replace('/','')
        target_path = target.split(':')[2]
    
    if target_path.endswith('/'):
        if source_name:
            target_path = target_path + source_name
    
    transfer_response = None
    
    
    # source path ends with '/'
    if source_name == '':
        isFolder = True
    
    if transferObject.options:
        if 'recursive' in transferObject.options:
            if transferObject.options['recursive'] == "True":
                isFolder = True
    
    time = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
    
    try:
            
        tdata = TransferData(transfer_client, source_endpoint_id,
                                        target_endpoint_id,
                                        label= 'RDSDS ' + time,
                                        sync_level="checksum")
        
        
        if isFolder:
            tdata.add_item(source_path, target_path, recursive=True)
        else:
            tdata.add_item(source_path, target_path)
            
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



async def get_transfer_globus_list(transfer_client: TransferClient, globus_item_count: int):
    """This function gets list of globus transfers for an user"""
    #transfer_client = await get_transfer_client(request)
    transfer_response = None
    
    try:
        transfer_result_dict= []    
        transfer_result = transfer_client.task_list(num_results=globus_item_count)
        #logging.info(transfer_result)
        for task in transfer_result:
            this_task_details = {'task_id':  task["task_id"]}
            this_task_details['source_endpoint'] = task["source_endpoint"]
            this_task_details['destination_endpoint'] = task["destination_endpoint"]
            transfer_result_dict.append(this_task_details)
        
        logging.info(transfer_result_dict)
        #transfer_result_json = json.loads(str(transfer_result_dict))
        transfer_response = {'globus_response': transfer_result_dict}
        #logging.info(transfer_response)
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
        transfer_response = {'globus_response': transfer_result}
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
