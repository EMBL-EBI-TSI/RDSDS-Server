import json
from starlette.requests import Request
from app.models.service import Service
from app.core.config import SERVICE_INFO_CONTACTURL, SERVICE_INFO_ENVIRONMENT, SERVICE_INFO_VERSION, SERVICE_INFO_CREATEDAT
from datetime import datetime

class ServiceInfo:
    service: Service = None

serviceInfo = ServiceInfo()

def create_service_info():
    with open('service-info.json') as service_info_json:
        data = json.load(service_info_json)
        service_info = Service(**data)
        service_info.contactUrl = SERVICE_INFO_CONTACTURL
        service_info.environment = SERVICE_INFO_ENVIRONMENT
        service_info.version = SERVICE_INFO_VERSION
        service_info.createdAt = SERVICE_INFO_CREATEDAT
        service_info.updatedAt = datetime.now().strftime("%d-%m-%y")
        serviceInfo.service = service_info
        
async def get_service_info(request: Request):      
    service_info = serviceInfo.service
    service_info.documentationUrl = request.headers['host'] + "/docs"
    return service_info