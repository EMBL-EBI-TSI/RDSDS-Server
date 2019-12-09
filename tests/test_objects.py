import logging
from starlette.testclient import TestClient
from main import app
from app.models.objects import DrsObject
from app.api.endpoints.objects import router as api_router

#api_client = TestClient(app)

def test_get_object_success():
    with TestClient(app) as api_client:
        response = api_client.get("/ga4gh/drs/v1/objects/0430d58d1199abc6310c7b51fedac148cc3b2d08c4c2dd5f40861e6ef930d7cf1502b92fa945a625acf80ef1dd2d3ea68d6b80e45043ec212f8f891fe2e48b91")
        assert response.status_code == 200
        drsObject = DrsObject(**response.json())
        assert drsObject.id == '0430d58d1199abc6310c7b51fedac148cc3b2d08c4c2dd5f40861e6ef930d7cf1502b92fa945a625acf80ef1dd2d3ea68d6b80e45043ec212f8f891fe2e48b91'
        
def test_get_object_404():
    with TestClient(app) as api_client:
        response = api_client.get("/ga4gh/drs/v1/objects/test")
        assert response.status_code == 404
        assert response.json().get('msg') == 'Requested DrsObject was not found'
    
