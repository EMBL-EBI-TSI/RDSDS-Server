from pydantic import BaseModel

class ServiceOrganization(BaseModel):
    name: str
    url: str

class Service(BaseModel):
    id: str
    name: str
    type: str
    organization: str
    version: str
    description: str = None
    organization: ServiceOrganization = None
    contactUrl: str = None
    documentationUrl: str = None
    createdAt: str = None
    updatedAt: str = None
    environment: str = None
    version: str = None



