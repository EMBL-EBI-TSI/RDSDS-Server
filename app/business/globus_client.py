from globus_sdk import ConfidentialAppAuthClient
import logging
from app.core.config import APP_CLIENT_ID, APP_CLIENT_SECRET

class GlobusClient:
    client: ConfidentialAppAuthClient = None

globus = GlobusClient()

def load_app_client():
    globus.client =  ConfidentialAppAuthClient(
        APP_CLIENT_ID, APP_CLIENT_SECRET)
    
