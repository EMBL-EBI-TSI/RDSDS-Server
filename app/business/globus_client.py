from globus_sdk import ConfidentialAppAuthClient
import logging
from app.core.config import GLOBUS_CLIENT_ID, GLOBUS_CLIENT_SECRET

class GlobusClient:
    client: ConfidentialAppAuthClient = None

globus = GlobusClient()

def load_app_client():
    globus.client =  ConfidentialAppAuthClient(
        GLOBUS_CLIENT_ID, GLOBUS_CLIENT_SECRET)
    
