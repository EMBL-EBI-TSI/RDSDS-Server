import logging
from globus_sdk import ConfidentialAppAuthClient,ClientCredentialsAuthorizer,TransferClient
from starlette.testclient import TestClient
from main import app
from app.core.config import GLOBUS_CLIENT_ID, GLOBUS_CLIENT_SECRET
from app.business.globus import create_transfer_globus, get_transfer_globus, get_transfer_globus_list
from app.business.transfer import get_globus_source_from_object, check_if_bundle
from app.models.transfer import TransferBase

#api_client = TestClient(app)
def get_client_credential_transfer_client():
    client =  ConfidentialAppAuthClient(GLOBUS_CLIENT_ID, GLOBUS_CLIENT_SECRET)
    scopes = "urn:globus:auth:scope:transfer.api.globus.org:all"
    cc_authorizer = ClientCredentialsAuthorizer(client, scopes)
    transfer_client = TransferClient(authorizer=cc_authorizer)
    return transfer_client

transfer_client = get_client_credential_transfer_client()

rdsds_tracking_id = None
    
async def test_create_transfer_globus_source():
    transferDict = {
      "object_id": "",
      "source": "globus://eb62ae5a-789a-11e9-b7f9-0a37f382de32:/Transfer_test_folder/source/test_1",
      "target": "globus://eb62ae5a-789a-11e9-b7f9-0a37f382de32:/Transfer_test_folder/target/test_1",
      "transfer_type": "globus",
      "options": {
        "recursive": "True"
      }
    }
    
    transferObject = TransferBase(**transferDict)
    
    transfer_response = await create_transfer_globus(transferObject=transferObject, transfer_client=transfer_client)
    logging.info(transfer_response)
    assert transfer_response['status'] == 200
    return transfer_response['rdsds_tracking_id']


async def test_create_transfer_globus_object():
    transferDict = {
      "object_id": "959c4e68e109e4e765d92bfe76dfbf26e20945030b336a1c4772a6366b44737cfefa9c1fc4bd0381290c083bf58378bcebf98c3d08f4e7ee1f4ce5cc09c716f5",
      "target": "globus://eb62ae5a-789a-11e9-b7f9-0a37f382de32:/Transfer_test_folder/target/",
      "transfer_type": "globus"
    }
    
    transferObject = TransferBase(**transferDict)
    
    transferObject.source = 'globus://fd9c190c-b824-11e9-98d7-0a63aa6b37da:/gridftp/pub/databases/eva/PRJEB27093'
    isFolder = True
    transfer_response = await create_transfer_globus(transferObject, transfer_client, isFolder)
    logging.info(transfer_response)
    assert transfer_response['status'] == 200
    return transfer_response['rdsds_tracking_id']    
        
async def test_get_transfer_globus():
    rdsds_tracking_id = await test_create_transfer_globus_source()
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
