from pydantic import BaseModel
from enum import Enum

class Checksum(BaseModel):
    type: str
    checksum: str


class AccessMethodEnum(str, Enum):
    s3 = 's3'
    gs = 'gs'
    ftp = 'ftp'
    #TODO: Update spec for sftp support
    sftp = 'sftp'
    gsiftp = 'gsiftp'
    globus = 'globus'
    htsget = 'htsget'
    https = 'https'
    file = 'file'


class AccessURL(BaseModel):
    url: str
    headers: Dict[str, str] = None


class AccessMethod(BaseModel):
    type: AccessMethodEnum
    access_url: AccessURL
    access_id: str = None
    region: str = None


class ContentsObject(BaseModel):
    name: str
    #TODO: Fix id has to be required in spec
    id: str
    # TODO: Add type field in spec
    # type: str
    drs_uri: str = None
    contents: List['ContentsObject'] = None

class DrsObject(BaseModel):
    id: str
    name: str
    self_uri: str
    size: int
    created_time: datetime = None
    updated_time: datetime = None
    version: str = None
    mime_type: str = None
    checksums: List[Checksum] = []
    access_methods: List[AccessMethod] = []
    contents: List[ContentsObject] = []
    description: str = None
    aliases: List[str] = None

class Error(BaseModel):
    msg: str
    status_code: int = 500