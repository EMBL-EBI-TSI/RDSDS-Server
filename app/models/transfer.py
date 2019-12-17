from pydantic import BaseModel
from datetime import datetime
from typing import Dict
from enum import Enum

class TransferType(str, Enum):
    GLOBUS = 'globus'
    S3 = 's3'
    GS = 'gs'
    #ftp = 'ftp'
    #sftp = 'sftp'
    GSIFTP = 'gsiftp'
    #htsget = 'htsget'
    #https = 'https'
    #file = 'file'
    

class TransferBase(BaseModel):
    object_id: str = None
    source: str = None
    target: str
    transfer_type: TransferType
    options: Dict[str, str] = None
    
class TransferStatus(TransferBase):
    created_time: datetime = None
    status: str
    
    
class TransferResponse(BaseModel):
    globus_response: Dict
    status: str
    rdsds_tracking_id: str
    globus_status_url: str
    
    