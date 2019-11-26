import logging
from globus_sdk import ConfidentialAppAuthClient,ClientCredentialsAuthorizer,TransferClient
from starlette.testclient import TestClient
from main import app
from app.core.config import APP_CLIENT_ID, APP_CLIENT_SECRET
from app.business.transfer import create_transfer_globus, get_transfer_globus, get_transfer_globus_list
from app.models.transfer import TransferBase

#api_client = TestClient(app)
def get_client_credential_transfer_client():
    client =  ConfidentialAppAuthClient(APP_CLIENT_ID, APP_CLIENT_SECRET)
    scopes = "urn:globus:auth:scope:transfer.api.globus.org:all"
    cc_authorizer = ClientCredentialsAuthorizer(client, scopes)
    transfer_client = TransferClient(authorizer=cc_authorizer)
    return transfer_client

transfer_client = get_client_credential_transfer_client()

rdsds_tracking_id = None
    
async def test_create_transfer_globus():
    transferDict = {
      "object_id": "string",
      "source": "/Transfer_test_folder/source/test_1",
      "target": "/Transfer_test_folder/target/test_1",
      "transfer_type": "globus",
      "options": {
        "source_endpoint": "eb62ae5a-789a-11e9-b7f9-0a37f382de32",
        "destination_endpoint": "eb62ae5a-789a-11e9-b7f9-0a37f382de32",
        "recursive": "True"
      }
    }
    
    transferObject = TransferBase(**transferDict)
    
    transfer_response = await create_transfer_globus(transferObject=transferObject, transfer_client=transfer_client)
    logging.info(transfer_response)
    assert transfer_response['status'] == 200
    return transfer_response['rdsds_tracking_id']
    
        
async def test_get_transfer_globus():
    rdsds_tracking_id = await test_create_transfer_globus()
    rdsds_tracking_id = rdsds_tracking_id.replace('globus-','')
    transfer_response = await get_transfer_globus(rdsds_tracking_id, transfer_client)
    logging.info(transfer_response)
    assert transfer_response['status'] == 200

async def test_get_transfer_list_globus():
    transfer_response = await get_transfer_globus_list(transfer_client, 10)
    logging.info(transfer_response)
    if 'globus_response' in transfer_response:
        assert True
    else:
        assert False
